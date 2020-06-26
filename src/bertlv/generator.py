import io
import os
import xml.dom.minidom

from abc import ABC, abstractmethod
from typing import BinaryIO
from xml.etree import ElementTree

from .tree import TlvNode, Tree


class GeneratorBase(ABC):
    @abstractmethod
    def close(self) -> bytes:
        """Close the generator and return the written bytes."""

    @abstractmethod
    def write(self, node: TlvNode) -> None:
        """Write the TLV node using the generator."""


class BinaryGenerator(GeneratorBase):
    def __init__(self):
        self.stream = io.BytesIO()

    def close(self) -> bytes:
        """Close the generator and return the written bytes."""
        try:
            buffer = self.stream.getvalue()
        finally:
            self.stream.close()
        return buffer

    def write(self, node: TlvNode) -> None:
        """Write the TLV node using the generator."""
        data = self._build(node)
        self.stream.write(data)

    def _build(self, node: TlvNode) -> bytes:
        tag = node.tag.identifier
        if node.is_constructed():
            value = self._build_children(node)
            length = self._length_as_bytes(len(value))
        else:
            value = node.value
            length = self._length_as_bytes(node.length)
        return tag + length + value

    def _build_children(self, node: TlvNode) -> bytes:
        data = bytearray()
        for child in node.children:
            data += self._build(child)
        return data

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


class XmlGenerator(GeneratorBase):
    def __init__(self):
        self.root = ElementTree.Element("Tlv")

    def close(self) -> bytes:
        """Close the generator and return the written bytes."""
        stream = io.BytesIO()
        try:
            stream.write(self._prettify(self.root))
        finally:
            self.root = ElementTree.Element("Tlv")
        return stream.getvalue()

    def write(self, node: TlvNode) -> None:
        """Write the TLV node using the generator."""
        self._build(node, self.root)

    def _build(self, node: TlvNode, parent: ElementTree.Element) -> None:
        tag_attr = "Primitive"
        if node.is_constructed():
            tag_attr = "Element"
        element = ElementTree.SubElement(parent, tag_attr)
        self._build_tag(node, element)
        if node.is_constructed():
            self._build_children(node, element)
        else:
            self._build_value(node, element)

    @staticmethod
    def _build_tag(node: TlvNode, element: ElementTree.Element) -> None:
        element.set("Tag", node.tag.to_hex())

    @staticmethod
    def _build_value(node: TlvNode, element: ElementTree.Element) -> None:
        try:
            text = node.value.decode("utf-8")
        except UnicodeError:
            text = None
        if text and text.isprintable():
            element.set("Type", "ASCII")
            element.text = text
        else:
            element.set("Type", "Hex")
            element.text = node.value.hex().upper()

    def _build_children(self, node: TlvNode, element: ElementTree.Element) -> None:
        for child in node.children:
            self._build(child, element)

    @staticmethod
    def _prettify(element: ElementTree.Element) -> bytes:
        """Return a pretty-printed XML byte-string for the element. """
        string = ElementTree.tostring(element, "utf-8")
        document = xml.dom.minidom.parseString(string)
        return document.toprettyxml("  ", os.linesep).encode("utf-8")


def generate(fp: BinaryIO, tree: Tree, generator: GeneratorBase) -> None:
    """Generate the tree and write it to the file-like object fp."""
    for node in tree.children:
        generator.write(node)
    fp.write(generator.close())


def generate_bytes(tree: Tree, generator: GeneratorBase) -> bytes:
    """Generate the tree and return the data."""
    fp = io.BytesIO()
    generate(fp, tree, generator)
    return fp.getvalue()
