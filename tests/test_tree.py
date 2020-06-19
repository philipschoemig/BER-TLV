import pytest

from bertlv.tag import Tag
from bertlv.tree import TlvNode, Tree


class TestTlvNode:
    def test_init(self):
        node = TlvNode(Tag.from_hex("FF60"))
        assert str(node) == "TlvNode('/ff60', tag=ff60)"

    def test_value(self):
        node = TlvNode(Tag.from_hex("5F20"), b"\x11\x22\x33")
        assert node.dump() == "5f20: 112233"

    def test_value_with_constructed_node(self):
        with pytest.raises(
            RuntimeError, match="Can not set value on constructed TLV node",
        ):
            TlvNode(Tag.from_hex("FF60"), b"\x11\x22\x33")

        node = TlvNode(Tag.from_hex("FF60"))
        with pytest.raises(
            RuntimeError, match="Can not set value on constructed TLV node",
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
            RuntimeError, match="Can not attach to primitive TLV node",
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
            RuntimeError, match="Can not attach to primitive TLV node",
        ):
            TlvNode(Tag.from_hex("DF01"), children=children)


class TestTree:
    def test_init(self):
        tree = Tree()
        assert str(tree) == "Tree('/Root', tag=Root)"

    def test_dump(self):
        children = [TlvNode(Tag.from_hex("5F20"), b"\x11\x22\x33")]
        tree = Tree(children)
        assert (
            tree.dump()
            == """Root
└── 5f20: 112233"""
        )
