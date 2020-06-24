from enum import Enum
from functools import total_ordering
from xml.etree import ElementTree

from . import config


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

    def __init__(self, identifier: bytes, *, force_constructed: bool = False):
        self._check_tag(identifier)
        self.identifier = identifier
        self._force_constructed = force_constructed

    def __repr__(self) -> str:
        return self.identifier.hex()

    def __str__(self) -> str:
        return f"0x{self.identifier.hex()}"

    def __eq__(self, other: "Tag"):
        return repr(self) == repr(other)

    def __lt__(self, other: "Tag"):
        return repr(self) < repr(other)

    @property
    def tag_class(self) -> TagClass:
        # In the initial octet, bits 7-8 encode the class
        class_bits = (self.identifier[0] & self.CLASS_BITMASK) >> 6
        return TagClass(class_bits)

    @property
    def tag_type(self) -> TagType:
        # In the initial octet, bit 6 encodes the type
        type_bits = (self.identifier[0] & self.TYPE_BITMASK) >> 5
        return TagType(type_bits)

    def is_constructed(self) -> bool:
        """Return true if the tag is constructed otherwise false."""
        if self.tag_type == TagType.CONSTRUCTED or self._force_constructed:
            return True
        return False

    def to_int(self) -> int:
        """Return an integer representing a tag."""
        return int.from_bytes(self.identifier, byteorder="big")

    def to_hex(self) -> str:
        """Return a hex string representing a tag."""
        return "0x" + self.identifier.hex().upper()

    def to_xml(self, element: ElementTree.Element) -> ElementTree.Element:
        """Return an XML element representing a tag."""
        element.set("Tag", self.to_hex())
        return element

    @classmethod
    def from_int(cls, tag: int, *, force_constructed: bool = False) -> "Tag":
        """Return the tag represented by the given integer."""
        length = (tag.bit_length() + 7) // 8
        return cls(
            tag.to_bytes(length, byteorder="big"), force_constructed=force_constructed
        )

    @classmethod
    def from_hex(cls, tag: str, *, force_constructed: bool = False) -> "Tag":
        """Return the tag represented by the given hex string."""
        if tag.startswith("0x"):
            tag = tag[2:]
        tag = tag.lstrip("0")
        return cls(bytes.fromhex(tag), force_constructed=force_constructed)

    @staticmethod
    def _check_tag(octets: bytes):
        """Check the tag octets against the Basic encoding rules of ASN.1 (see ISO/IEC 8825)."""
        if len(octets) == 0:
            raise ValueError("tag must not be empty")
        if octets[0] & 0x1F == 0x1F:
            if len(octets) == 1:
                raise ValueError(f"tag is missing subsequent octets: {octets.hex()}")
            for index, byte in enumerate(octets[1:], start=1):
                if index == 1 and byte == 0x80 and config.strict_checking:
                    raise ValueError(
                        "tag has first subsequent octet where bits 7 to 1 are all "
                        f"zero: {octets.hex()}"
                    )
                if index + 1 < len(octets) and byte & 0x80 != 0x80:
                    raise ValueError(
                        f"tag has subsequent octet where bit 1 is not set: {octets.hex()}"
                    )
                if index + 1 == len(octets) and byte & 0x80 == 0x80:
                    raise ValueError(
                        f"tag is missing subsequent octets: {octets.hex()}"
                    )


class RootTag(Tag):
    def __init__(self):
        super().__init__(b"\x00", force_constructed=True)

    def __repr__(self) -> str:
        return "root"

    def __str__(self) -> str:
        return "root"
