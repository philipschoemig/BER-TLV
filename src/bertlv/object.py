import os
from abc import ABC, abstractmethod
from functools import total_ordering
from typing import List, Optional, Type, Union
from xml.etree import ElementTree

from .stream import Stream
from .tag import Tag


@total_ordering
class TlvObject(ABC):
    def __init__(self, tag: Tag, value: Optional[bytes] = None):
        self.tag = tag
        self.value = value

    def __eq__(self, other: "TlvObject"):
        return self.tag == other.tag

    def __lt__(self, other: "TlvObject"):
        return self.tag < other.tag

    @property
    def length(self) -> int:
        if self.value:
            return len(self.value)
        return 0

    @abstractmethod
    def find(self, pattern):
        """Find a child of a TLV object using the given pattern."""

    @abstractmethod
    def build(self) -> bytes:
        """Return an array of bytes representing a TLV object."""

    @abstractmethod
    def to_xml(self, parent: ElementTree.Element) -> ElementTree.Element:
        """Return an XML element representing a TLV object."""

    @abstractmethod
    def dump(self, indent: Optional[Union[int, str]] = None, level: int = 0) -> str:
        """Return a string with indentation representing a TLV object."""

    @classmethod
    @abstractmethod
    def parse(cls, tlv: Stream) -> "TlvObject":
        """Return the TLV object parsed from the given TLV stream."""

    @classmethod
    @abstractmethod
    def from_xml(cls, element: ElementTree.Element) -> "TlvObject":
        """Return the TLV object represented by the given XML element."""

    @staticmethod
    def get_object(tag: Tag) -> Type["TlvObject"]:
        """Return the TLV object type matching the given TLV tag."""
        if tag.is_constructed():
            return Element
        else:
            return Primitive

    @staticmethod
    def _parse_length(tlv: Stream) -> int:
        try:
            length = next(tlv)
            if length & 0x80 == 0x80:
                length_data = bytes([next(tlv) for _ in range(length & 0x7F)])
                length = int(length_data.hex(), 16)
        except StopIteration as e:
            raise RuntimeError(
                f"Error while parsing TLV length. Offset: {tlv.index} "
                f"Remaining data: {tlv.remaining.hex()}"
            ) from e
        return length

    @staticmethod
    def _parse_value(tlv: Stream) -> bytes:
        try:
            length = TlvObject._parse_length(tlv)
            value = bytearray([next(tlv) for _ in range(length)])
        except StopIteration as e:
            raise RuntimeError(
                f"Error while parsing TLV value. Offset: {tlv.index} "
                f"Remaining data: {tlv.remaining.hex()}"
            ) from e
        return value

    @staticmethod
    def _length_as_bytes(length: int) -> bytes:
        """Return the given length as TLV bytes."""
        number_of_bytes = 1
        if length:
            number_of_bytes = (length.bit_length() + 7) // 8
        length_bytes = bytearray()
        if number_of_bytes > 1 or length >= 0x80:
            length_bytes.append(0x80 + number_of_bytes)
        length_bytes += length.to_bytes(number_of_bytes, byteorder="big")
        return length_bytes


class Element(TlvObject):
    def __init__(self, tag: Tag, children: List[TlvObject] = None):
        if not tag.is_constructed():
            raise RuntimeError(
                f"Element class expects a constructed TLV tag, "
                f"but got a primitive tag: {tag}"
            )
        super().__init__(tag)
        self._list = children or list()

    def __iter__(self):
        return iter(self._list)

    def __str__(self):
        list_str = [str(child) for child in self._list]
        return f"Element {self.tag}: [{', '.join(list_str)}]"

    def find(self, pattern):
        tag, *rest = pattern.split("/", maxsplit=1)
        tag = tag.lower()
        for child in self._list:
            if tag.lower() == repr(child.tag):
                if rest:
                    return child.find(*rest)
                return child
        return None

    def append(self, child: TlvObject) -> None:
        """Append a child TLV object to this TLV element."""
        self._list.append(child)

    def build(self) -> bytes:
        children_tlv = bytearray()
        if self._list:
            for child in self._list:
                children_tlv += child.build()
        tlv = bytearray()
        tlv += self.tag.build()
        tlv += self._length_as_bytes(len(children_tlv))
        if children_tlv:
            tlv += children_tlv
        return tlv

    def to_xml(self, parent: ElementTree.Element) -> ElementTree.Element:
        element = self.tag.to_xml(ElementTree.SubElement(parent, "Element"))
        if self._list:
            for child in self._list:
                child.to_xml(element)
        return element

    def dump(self, indent: Optional[Union[int, str]] = None, level: int = 0) -> str:
        if not indent:
            indent = ""
        if isinstance(indent, int):
            indent = " " * indent
        children_str = ""
        for child in self._list:
            children_str += child.dump(indent, level + 1)
        return f"{indent * level}{self.tag}{os.linesep}{children_str}"

    @classmethod
    def parse(cls, tlv: Stream) -> "Element":
        tag = Tag.parse(tlv)
        instance = None
        if tag.is_constructed():
            length = cls._parse_length(tlv)
            end = tlv.index + length
            children = []
            while tlv.index < end:
                with tlv:
                    child_tag = Tag.parse(tlv)
                child = super().get_object(child_tag).parse(tlv)
                if child:
                    children.append(child)
            instance = cls(tag, children)
        return instance

    @classmethod
    def from_xml(cls, element: ElementTree.Element) -> "Element":
        tag = Tag.from_xml(element)
        instance = None
        if element.tag == "Element":
            children = []
            for sub_element in element:
                child_tag = Tag.from_xml(sub_element)
                child = super().get_object(child_tag).from_xml(sub_element)
                if child:
                    children.append(child)
            instance = cls(tag, children)
        return instance


class Primitive(TlvObject):
    def __init__(self, tag: Tag, value: bytes):
        if tag.is_constructed():
            raise RuntimeError(
                f"Primitive class expects a primitive TLV tag, "
                f"but got a constructed tag: {tag}"
            )
        super().__init__(tag, value)

    def __str__(self):
        return f"Primitive {self.tag}: {self.value.hex() if self.value else 'Empty'}"

    def find(self, pattern):
        return None

    def build(self) -> bytes:
        tlv = bytearray()
        tlv += self.tag.build()
        tlv += self._length_as_bytes(self.length)
        if self.value:
            tlv += self.value
        return tlv

    def to_xml(self, parent: ElementTree.Element) -> ElementTree.Element:
        element = self.tag.to_xml(ElementTree.SubElement(parent, "Primitive"))
        if self.value and self.value.isalnum():
            element.set("Type", "ASCII")
            element.text = self.value.decode("iso8859_15")
        else:
            element.set("Type", "Hex")
            element.text = self.value.hex().upper()
        return element

    def dump(self, indent: Optional[Union[int, str]] = None, level: int = 0) -> str:
        if not indent:
            indent = ""
        if isinstance(indent, int):
            indent = " " * indent
        return f"{indent * level}{self.tag}: {self.value.hex()}{os.linesep}"

    @classmethod
    def parse(cls, tlv: Stream) -> "Primitive":
        tag = Tag.parse(tlv)
        instance = None
        if not tag.is_constructed():
            value = cls._parse_value(tlv)
            instance = cls(tag, value)
        return instance

    @classmethod
    def from_xml(cls, element: ElementTree.Element) -> "Primitive":
        tag = Tag.from_xml(element)
        instance = None
        if element.tag == "Primitive":
            text = "".join(element.text.split())
            if element.get("Type") == "Hex" or not element.get("Type"):
                try:
                    if len(text) % 2 == 1:
                        text = text.rjust(len(text) + 1, "0")
                    value = bytearray.fromhex(text)
                except Exception as e:
                    raise RuntimeError(
                        f"Invalid Value for tag {tag}: {text} - {e}"
                    ) from e
            elif element.get("Type") == "ASCII":
                value = bytearray(text, "iso8859_15")
            else:
                raise RuntimeError(
                    f"Invalid Type for a Primitive: {element.get('Type')}"
                )
            instance = cls(tag, value)
        return instance
