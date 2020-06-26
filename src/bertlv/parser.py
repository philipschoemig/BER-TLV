import io

from abc import ABC, abstractmethod
from distutils.util import strtobool
from typing import BinaryIO, Optional
from xml.etree import ElementTree

from .stream import BufferedStream
from .tag import Tag
from .tree import BuilderBase, TlvError, TlvNode, Tree, TreeBuilder


class ParserError(TlvError):
    def __init__(
        self,
        message: str,
        *,
        tag: Tag = None,
        offset: int = None,
        element: ElementTree.Element = None,
    ):
        kwargs = {}
        if tag is not None:
            kwargs["tag"] = repr(tag)
        if offset is not None:
            kwargs["offset"] = str(offset)
        if element is not None:
            string = ElementTree.tostring(element, encoding="unicode")
            kwargs["element"] = f"'{string.rstrip()}'"
        super().__init__(f"error while parsing the {message}", **kwargs)


class InsufficientDataError(ParserError):
    def __init__(
        self, message: str, **kwargs,
    ):
        super().__init__(f"insufficient data to parse the {message}", **kwargs)


class ParserBase(ABC):
    def __init__(self, *, target: BuilderBase = None):
        self.target = target or TreeBuilder()

    @abstractmethod
    def close(self) -> Tree:
        """Close the parser and return the tree."""

    @abstractmethod
    def feed(self, data: bytes) -> None:
        """Feed data to the parser."""


class BinaryParser(ParserBase):
    def __init__(self, *, target: BuilderBase = None):
        super().__init__(target=target)
        self.stream = BufferedStream()

    def close(self) -> Tree:
        """Close the parser and return the tree."""
        try:
            while not self.stream.is_eof():
                self._parse()
        finally:
            self.stream.close()
        return self.target.close()

    def feed(self, data: bytes) -> None:
        """Feed data to the parser."""
        self.stream.push(data)
        try:
            while not self.stream.is_eof():
                with self.stream.rollback(InsufficientDataError):
                    self._parse()
        except InsufficientDataError:
            pass

    def _parse(self) -> TlvNode:
        tag = self._parse_tag()
        length = self._parse_length(tag)
        if self.stream.size() < length:
            message = "value"
            if tag.is_constructed():
                message = "constructed value"
            raise InsufficientDataError(message, tag=tag, offset=self.stream.tell())

        self.target.start(tag)
        if tag.is_constructed():
            self._parse_children(length)
        else:
            data = self._parse_value(tag, length)
            self.target.data(data)
        return self.target.end(tag)

    def _parse_tag(self) -> Tag:
        try:
            number = bytearray([next(self.stream)])
            if number[-1] & 0x1F == 0x1F:
                number.append(next(self.stream))
                while number[-1] & 0x80 == 0x80:
                    number.append(next(self.stream))
            tag = Tag(number)
        except StopIteration as e:
            raise InsufficientDataError("tag", offset=self.stream.tell()) from e
        except Exception as e:
            raise ParserError("tag", offset=self.stream.tell()) from e
        return tag

    def _parse_length(self, tag: Tag) -> int:
        try:
            length = next(self.stream)
            if length & 0x80 == 0x80:
                length_data = bytes([next(self.stream) for _ in range(length & 0x7F)])
                length = int(length_data.hex(), 16)
        except StopIteration as e:
            raise InsufficientDataError(
                "length", tag=tag, offset=self.stream.tell()
            ) from e
        except Exception as e:
            raise ParserError("length", tag=tag, offset=self.stream.tell()) from e
        return length

    def _parse_value(self, tag: Tag, length: int) -> bytes:
        try:
            value = bytearray([next(self.stream) for _ in range(length)])
        except StopIteration as e:
            raise InsufficientDataError(
                "value", tag=tag, offset=self.stream.tell()
            ) from e
        except Exception as e:
            raise ParserError("value", tag=tag, offset=self.stream.tell()) from e
        return value

    def _parse_children(self, length: int) -> None:
        end = self.stream.tell() + length
        while self.stream.tell() < end:
            self._parse()


class XmlParser(ParserBase):
    def __init__(self, *, target: BuilderBase = None):
        super().__init__(target=target)
        self.parser = ElementTree.XMLPullParser(["start", "end"])

    def close(self) -> Tree:
        """Close the parser and return the tree."""
        try:
            for event in self.parser.read_events():
                self._parse(event)
        finally:
            self.parser.close()
        return self.target.close()

    def feed(self, data: bytes) -> None:
        """Feed data to the parser."""
        self.parser.feed(data)
        for event in self.parser.read_events():
            self._parse(event)

    def _parse(self, event: (str, ElementTree.Element)) -> Optional[TlvNode]:
        event_type, element = event
        if element.tag.capitalize() == "Tlv":
            return None
        tag = self._parse_tag(element)
        node = None
        if event_type == "start":
            self.target.start(tag)
        elif event_type == "end":
            if not tag.is_constructed():
                data = self._parse_value(tag, element)
                self.target.data(data)
            node = self.target.end(tag)
        return node

    @staticmethod
    def _parse_tag(element: ElementTree.Element) -> Tag:
        try:
            tag_attr = element.get("Tag")
            if not tag_attr:
                raise ValueError("missing 'Tag' attribute")

            force_constructed = False
            if element.tag == "Element":
                # noinspection PyTypeChecker
                force_constructed = strtobool(element.get("Force", "False"))

            tag = Tag.from_hex(tag_attr, force_constructed=force_constructed)
            if tag.is_constructed():
                assert element.tag == "Element"
            else:
                assert element.tag == "Primitive"
        except Exception as e:
            raise ParserError("tag", element=element) from e
        return tag

    @staticmethod
    def _parse_value(tag: Tag, element: ElementTree.Element) -> bytes:
        try:
            value = bytes()
            if element.text:
                text = "".join(element.text.split())
                if element.get("Type") == "Hex" or not element.get("Type"):
                    if len(text) % 2 == 1:
                        text = text.rjust(len(text) + 1, "0")
                    value = bytearray.fromhex(text)
                elif element.get("Type") == "ASCII":
                    value = bytearray(text, "iso8859_15")
                else:
                    raise ValueError(
                        f"invalid 'Type' attribute value: {element.get('Type')}"
                    )
        except Exception as e:
            raise ParserError("value", tag=tag, element=element) from e
        return value


def parse(fp: BinaryIO, parser: ParserBase) -> Tree:
    """Parse data read from the file-like object fp and return the tree."""
    while True:
        data = fp.read(8192)
        if not data:
            break
        parser.feed(data)
    return parser.close()


def parse_bytes(data: bytes, parser: ParserBase) -> Tree:
    """Parse data and return the tree."""
    return parse(io.BytesIO(data), parser)
