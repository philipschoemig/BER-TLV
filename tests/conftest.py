import os

import pytest

from bertlv.tag import Tag
from bertlv.tree import TlvNode, Tree, TreeBuilder


@pytest.fixture
def tlv_tree() -> Tree:
    """Return the test tree.

    Tree structure:
    root
    └── e1
        ├── 9f1e: 3136303231343337
        ├── ef
        │   ├── df0d: 4d3030302d4d5049
        │   └── df7f: 312d3232
        └── ef
            ├── df0d: 4d3030302d544553544f53
            └── df7f: 362d35
    """
    tree = Tree()
    xe1 = TlvNode(Tag.from_hex("e1"), parent=tree)
    TlvNode(Tag.from_hex("9f1e"), value=bytes.fromhex("3136303231343337"), parent=xe1)
    xef_1 = TlvNode(Tag.from_hex("ef"), parent=xe1)
    TlvNode(Tag.from_hex("df0d"), value=bytes.fromhex("4d3030302d4d5049"), parent=xef_1)
    TlvNode(Tag.from_hex("df7f"), value=bytes.fromhex("312d3232"), parent=xef_1)
    xef_2 = TlvNode(Tag.from_hex("ef"), parent=xe1)
    TlvNode(
        Tag.from_hex("df0d"),
        value=bytes.fromhex("4d3030302d544553544f53"),
        parent=xef_2,
    )
    TlvNode(Tag.from_hex("df7f"), value=bytes.fromhex("362d35"), parent=xef_2)
    return tree


@pytest.fixture
def tlv_dump():
    """Return the dump for the test tree."""
    return """root
└── e1
    ├── 9f1e: 3136303231343337
    ├── ef
    │   ├── df0d: 4d3030302d4d5049
    │   └── df7f: 312d3232
    └── ef
        ├── df0d: 4d3030302d544553544f53
        └── df7f: 362d35"""


@pytest.fixture
def tlv_builder():
    """Return the builder for the test tree."""
    builder = TreeBuilder()
    builder.start(Tag.from_hex("e1"))

    builder.start(Tag.from_hex("9f1e"))
    builder.data(bytes.fromhex("3136303231343337"))
    builder.end(Tag.from_hex("9f1e"))

    builder.start(Tag.from_hex("ef"))

    builder.start(Tag.from_hex("df0d"))
    builder.data(bytes.fromhex("4d3030302d4d5049"))
    builder.end(Tag.from_hex("df0d"))

    builder.start(Tag.from_hex("df7f"))
    builder.data(bytes.fromhex("312d3232"))
    builder.end(Tag.from_hex("df7f"))

    builder.end(Tag.from_hex("ef"))

    builder.start(Tag.from_hex("ef"))

    builder.start(Tag.from_hex("df0d"))
    builder.data(bytes.fromhex("4d3030302d544553544f53"))
    builder.end(Tag.from_hex("df0d"))

    builder.start(Tag.from_hex("df7f"))
    builder.data(bytes.fromhex("362d35"))
    builder.end(Tag.from_hex("df7f"))

    builder.end(Tag.from_hex("ef"))

    builder.end(Tag.from_hex("e1"))
    return builder


@pytest.fixture
def tlv_data_binary():
    """Return the binary data for the test tree as bytes."""
    return (
        b"\xe1\x35\x9f\x1e\x08\x31\x36\x30\x32\x31\x34\x33\x37\xef\x12\xdf"
        b"\x0d\x08\x4d\x30\x30\x30\x2d\x4d\x50\x49\xdf\x7f\x04\x31\x2d\x32"
        b"\x32\xef\x14\xdf\x0d\x0b\x4d\x30\x30\x30\x2d\x54\x45\x53\x54\x4f"
        b"\x53\xdf\x7f\x03\x36\x2d\x35"
    )


@pytest.fixture
def tlv_data_text(tlv_dump):
    """Return the text dump for the test tree as bytes."""
    return tlv_dump.encode("utf-8")


@pytest.fixture
def tlv_data_xml():
    """Return the XML data for the test tree as bytes."""
    data = """<?xml version="1.0" ?>
<Tlv>
  <Element Tag="0xE1">
    <Primitive Tag="0x9F1E" Type="ASCII">16021437</Primitive>
    <Element Tag="0xEF">
      <Primitive Tag="0xDF0D" Type="ASCII">M000-MPI</Primitive>
      <Primitive Tag="0xDF7F" Type="ASCII">1-22</Primitive>
    </Element>
    <Element Tag="0xEF">
      <Primitive Tag="0xDF0D" Type="ASCII">M000-TESTOS</Primitive>
      <Primitive Tag="0xDF7F" Type="ASCII">6-5</Primitive>
    </Element>
  </Element>
</Tlv>
"""
    # Convert newlines to OS line separator before encoding the string
    return data.replace("\n", os.linesep).encode("utf-8")


@pytest.fixture
def tlv_file_binary(tlv_data_binary, tmp_path):
    """Return the path to a binary file containing the test tree."""
    path = tmp_path / "expected.tlv"
    path.write_bytes(tlv_data_binary)
    return path


@pytest.fixture
def tlv_file_text(tlv_data_text, tmp_path):
    """Return the path to a text file containing the test tree."""
    path = tmp_path / "expected.txt"
    path.write_bytes(tlv_data_text)
    return path


@pytest.fixture
def tlv_file_xml(tlv_data_xml, tmp_path):
    """Return the path to an XML file containing the test tree."""
    path = tmp_path / "expected.xml"
    path.write_bytes(tlv_data_xml)
    return path
