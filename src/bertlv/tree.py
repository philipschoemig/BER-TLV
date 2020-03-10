from typing import List, Optional, Union
from xml.etree import ElementTree

from .object import TlvObject
from .stream import Stream
from .tag import Tag


class Tree:
    def __init__(self, children: List[TlvObject] = None):
        self._list = children or list()

    def __iter__(self):
        return iter(self._list)

    def __str__(self):
        list_str = [str(child) for child in self._list]
        return f"Tree: [{', '.join(list_str)}]"

    def find(self, pattern):
        """Find a child of a TLV object using the given pattern."""
        tag, *rest = pattern.split("/", maxsplit=1)
        tag = tag.lower()
        for child in self._list:
            if tag.lower() == repr(child.tag):
                if rest:
                    return child.find(*rest)
                return child
        return None

    def build(self) -> bytes:
        """Return an array of bytes representing a TLV tree."""
        tlv = bytearray()
        if self._list:
            for child in self._list:
                tlv += child.build()
        return tlv

    def to_xml(self) -> ElementTree.Element:
        """Return an XML element representing a TLV tree."""
        element = ElementTree.Element("Tlv")
        if self._list:
            for child in self._list:
                child.to_xml(element)
        return element

    def dump(self, indent: Optional[Union[int, str]] = None) -> str:
        """Return a string with indentation representing a TLV tree."""
        if not indent:
            indent = ""
        if isinstance(indent, int):
            indent = " " * indent
        children_str = ""
        for child in self._list:
            children_str += child.dump(indent, 0)
        return f"{children_str}"

    @classmethod
    def parse(cls, data: bytes) -> "Tree":
        """Return the TLV tree parsed from the given array of bytes."""
        children = []
        tlv = Stream(data)
        while not tlv.is_empty():
            with tlv:
                tag = Tag.parse(tlv)
            child = TlvObject.get_object(tag).parse(tlv)
            if child:
                children.append(child)
        return cls(children)

    @classmethod
    def from_xml(cls, root: ElementTree.Element) -> "Tree":
        """Return the TLV tree represented by the given XML element."""
        children = []
        for element in root:
            tag = Tag.from_xml(element)
            child = TlvObject.get_object(tag).from_xml(element)
            if child:
                children.append(child)
        return cls(children)
