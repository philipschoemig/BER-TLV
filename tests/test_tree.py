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
        assert node_5f20 == "5F20"

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

    def test_dump(self, tlv_dump, tlv_tree):
        assert tlv_tree.dump() == tlv_dump

    def test_dump_mapper(self, setup_mapper, tlv_dump_mapped, tlv_tree):
        assert tlv_tree.dump() == tlv_dump_mapped


class TestTreeBuilder:
    def test_init(self):
        builder = TreeBuilder()
        assert builder._current == builder._tree
        assert builder._tree == Tree()

    def test_close(self, tlv_builder, tlv_tree):
        assert tlv_builder.close() == tlv_tree

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
