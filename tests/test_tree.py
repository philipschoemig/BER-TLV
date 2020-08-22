import os

import pytest

from bertlv.tag import Tag
from bertlv.tree import TlvError, TlvNode, Tree, TreeBuilder


class TestTlvNode:
    def test_init(self):
        node = TlvNode(Tag.from_hex("FF60"))
        assert repr(node) == "TlvNode('/ff60', tag=ff60)"
        assert str(node) == "/ff60"

    def test_comparison(self):
        node_5f20 = TlvNode(Tag.from_hex("5F20"))
        node_5f20_data = TlvNode(Tag.from_hex("5F20"), b"\x11\x22\x33")
        assert node_5f20 == node_5f20_data

        node_5f21 = TlvNode(Tag.from_hex("5F21"))
        assert node_5f20 < node_5f21

    def test_value(self):
        node = TlvNode(Tag.from_hex("5F20"), b"\x11\x22\x33")
        assert node.dump() == "5f20: 112233"

    def test_value_with_constructed_node(self):
        with pytest.raises(
            TlvError, match="Can not set value on constructed node: tag ff60$",
        ):
            TlvNode(Tag.from_hex("FF60"), b"\x11\x22\x33")

        node = TlvNode(Tag.from_hex("FF60"))
        with pytest.raises(
            TlvError, match="Can not set value on constructed node: tag ff60$",
        ):
            node.value = b"\x11\x22\x33"

    def test_length(self):
        primitive = TlvNode(Tag.from_hex("5F20"), b"\x11\x22\x33")
        assert primitive.length == 3

        constructed = TlvNode(Tag.from_hex("FF60"))
        assert constructed.length == 0

    def test_parent(self):
        parent = TlvNode(Tag.from_hex("FF60"))
        node = TlvNode(Tag.from_hex("5F20"), b"\x11\x22\x33", parent=parent)
        assert node.dump() == "5f20: 112233"

    def test_parent_with_primitive_node(self):
        parent = TlvNode(Tag.from_hex("DF01"))
        with pytest.raises(
            TlvError, match="Can not attach to primitive node: tag df01$",
        ):
            TlvNode(Tag.from_hex("5F20"), b"\x11\x22\x33", parent=parent)

    def test_children(self):
        children = [TlvNode(Tag.from_hex("5F20"), b"\x11\x22\x33")]
        node = TlvNode(Tag.from_hex("FF60"), children=children)
        assert (
            node.dump()
            == """ff60
└── 5f20: 112233"""
        )

    def test_children_with_primitive_node(self):
        children = [TlvNode(Tag.from_hex("5F20"), b"\x11\x22\x33")]
        with pytest.raises(
            TlvError, match="Can not attach to primitive node: tag df01$",
        ):
            TlvNode(Tag.from_hex("DF01"), children=children)

    def test_resolve(self):
        x5f20 = TlvNode(Tag.from_hex("5F20"), b"\x11\x22\x33")
        xff60 = TlvNode(Tag.from_hex("FF60"), children=[x5f20])
        tree = Tree(children=[xff60])

        node = tree.resolve("ff60/5f20")
        assert node == x5f20

        node = tree.resolve("/root/ff60/5f20")
        assert node == x5f20

    def test_resolve_with_upper_case_path(self):
        x5f20 = TlvNode(Tag.from_hex("5F20"), b"\x11\x22\x33")
        xff60 = TlvNode(Tag.from_hex("FF60"), children=[x5f20])
        tree = Tree(children=[xff60])

        node = tree.resolve("FF60/5F20")
        assert node == x5f20

    def test_resolve_with_incorrect_path(self):
        tree = Tree()
        with pytest.raises(
            TlvError, match="Can not resolve path '5f20' from this node: tag root$",
        ):
            tree.resolve("5f20")


class TestTree:
    def test_init(self):
        tree = Tree()
        assert repr(tree) == "Tree('/root', tag=root)"
        assert str(tree) == "/root"

    def test_dump(self):
        assert _test_tree().dump() == _test_dump()


class TestTreeBuilder:
    def test_init(self):
        builder = TreeBuilder()
        assert builder._current == builder._tree
        assert builder._tree == Tree()

    def test_close(self):
        assert _test_builder().close() == _test_tree()

    def test_close_with_missing_end(self):
        builder = TreeBuilder()
        builder.start(Tag.from_hex("e1"))
        assert builder._current == TlvNode(Tag.from_hex("e1"))
        with pytest.raises(
            TlvError, match="Missing end tag for '/root/e1'$",
        ):
            builder.close()

    def test_end(self):
        builder = TreeBuilder()
        builder.start(Tag.from_hex("e1"))
        assert builder._current == TlvNode(Tag.from_hex("e1"))
        builder.end(Tag.from_hex("e1"))
        assert builder._current == builder._tree

    def test_end_with_tag_mismatch(self):
        builder = TreeBuilder()
        builder.start(Tag.from_hex("e1"))
        assert builder._current == TlvNode(Tag.from_hex("e1"))
        with pytest.raises(
            TlvError, match="End tag mismatch for '/root/e1', got e2$",
        ):
            builder.end(Tag.from_hex("e2"))

    def test_data(self):
        builder = TreeBuilder()
        builder.start(Tag.from_hex("df7f"))
        assert builder._current == TlvNode(Tag.from_hex("df7f"))
        builder.data(bytes.fromhex("3136303231343337"))
        assert builder._current == TlvNode(
            Tag.from_hex("df7f"), bytes.fromhex("3136303231343337")
        )
        builder.end(Tag.from_hex("df7f"))
        assert builder._current == builder._tree

    def test_start(self):
        builder = TreeBuilder()
        builder.start(Tag.from_hex("e1"))
        assert builder._current == TlvNode(Tag.from_hex("e1"))


def _test_builder():
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


def _test_tree() -> Tree:
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


def _test_binary_data():
    """Return the binary data for the test tree."""
    return (
        b"\xe1\x35\x9f\x1e\x08\x31\x36\x30\x32\x31\x34\x33\x37\xef\x12\xdf"
        b"\x0d\x08\x4d\x30\x30\x30\x2d\x4d\x50\x49\xdf\x7f\x04\x31\x2d\x32"
        b"\x32\xef\x14\xdf\x0d\x0b\x4d\x30\x30\x30\x2d\x54\x45\x53\x54\x4f"
        b"\x53\xdf\x7f\x03\x36\x2d\x35"
    )


def _test_xml_data():
    """Return the XML data for the test tree."""
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


def _test_dump():
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
