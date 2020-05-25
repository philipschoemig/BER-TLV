from enum import Enum
from functools import total_ordering
from xml.etree import ElementTree

from .stream import Stream


class TagClass(Enum):
    UNIVERSAL = 0  # 0b00000000
    APPLICATION = 1  # 0b01000000
    CONTEXT_SPECIFIC = 2  # 0b10000000
    PRIVATE = 3  # 0b11000000


class TagType(Enum):
    PRIMITIVE = 0  # 0b00000000
    CONSTRUCTED = 1  # 0b00100000


@total_ordering
class Tag:
    """This represents a TLV tag following the BER encoding."""

    CLASS_BITMASK = 0b11000000
    TYPE_BITMASK = 0b00100000

    def __init__(self, number: bytes):
        self.number = number

    def __repr__(self) -> str:
        return self.number.hex()

    def __str__(self) -> str:
        return f"0x{self.number.hex()}"

    def __eq__(self, other: "Tag"):
        return repr(self) == repr(other)

    def __lt__(self, other: "Tag"):
        return repr(self) < repr(other)

    @property
    def tag_class(self) -> TagClass:
        # In the initial octet, bits 7-8 encode the class
        class_bits = (self.number[0] & self.CLASS_BITMASK) >> 6
        return TagClass(class_bits)

    @property
    def tag_type(self) -> TagType:
        # In the initial octet, bit 6 encodes the type
        type_bits = (self.number[0] & self.TYPE_BITMASK) >> 5
        return TagType(type_bits)

    def is_constructed(self) -> bool:
        """Return true if the tag is constructed otherwise false."""
        if self.tag_type == TagType.CONSTRUCTED:
            return True
        return False

    def build(self) -> bytes:
        """Return an array of bytes representing a tag."""
        return self.number

    def to_int(self) -> int:
        """Return an integer representing a tag."""
        return int.from_bytes(self.number, byteorder="big")

    def to_hex(self) -> str:
        """Return a hex string representing a tag."""
        return "0x" + self.number.hex().upper()

    def to_xml(self, element: ElementTree.Element) -> ElementTree.Element:
        """Return an XML element representing a tag."""
        element.set("Tag", self.to_hex())
        return element

    @classmethod
    def parse(cls, tlv: Stream) -> "Tag":
        """Return the tag parsed from the given TLV stream."""
        try:
            tag = bytearray([next(tlv)])
            if tag[-1] & 0x1F == 0x1F:
                tag.append(next(tlv))
                while tag[-1] & 0x80 == 0x80:
                    tag.append(next(tlv))
        except StopIteration as e:
            raise RuntimeError(
                f"Error while parsing a TLV tag. Offset: {tlv.index} "
                f"Remaining data: {tlv.remaining.hex()}"
            ) from e
        return cls(tag)

    @classmethod
    def from_int(cls, tag: int) -> "Tag":
        """Return the tag represented by the given integer."""
        length = (tag.bit_length() + 7) // 8
        return cls(tag.to_bytes(length, byteorder="big"))

    @classmethod
    def from_hex(cls, tag: str) -> "Tag":
        """Return the tag represented by the given hex string."""
        if tag.startswith("0x"):
            tag = tag[2:]
        tag = tag.lstrip("0")
        return cls(bytes.fromhex(tag))

    @classmethod
    def from_xml(cls, element: ElementTree.Element) -> "Tag":
        """Return the tag represented by the given XML element."""
        tag_attr = element.get("Tag")
        if not tag_attr:
            raise RuntimeError(f"Element is missing 'Tag' attribute: {element.tag}")
        try:
            return cls.from_hex(tag_attr)
        except Exception as e:
            raise RuntimeError(f"Invalid Tag: {element.get('Tag')} - {e}") from e
