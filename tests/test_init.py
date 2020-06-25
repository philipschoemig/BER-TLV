import io

from bertlv import Tree, tree_from_binary, tree_from_xml, tree_to_binary, tree_to_xml
from bertlv.tag import Tag
from bertlv.tree import TlvNode


def test_tree_from_binary_with_bytes():
    data = test_tree_to_binary_with_bytes()
    tree_from_binary(data)
    tree_from_binary(bytearray(data))
    # noinspection PyTypeChecker
    tree_from_binary(memoryview(data))


def test_tree_from_binary_with_io(tmp_path):
    data = test_tree_to_binary_with_bytes()
    tree_from_binary(io.BytesIO(data))

    test_tree_to_binary_with_io(tmp_path)
    path = tmp_path / "test.tlv"
    with path.open("rb") as file:
        tree_from_binary(file)


def test_tree_from_xml_with_bytes():
    data = test_tree_to_xml_with_bytes()
    tree_from_xml(data)
    tree_from_xml(bytearray(data))
    # noinspection PyTypeChecker
    tree_from_xml(memoryview(data))


def test_tree_from_xml_with_io(tmp_path):
    data = test_tree_to_xml_with_bytes()
    tree_from_xml(io.BytesIO(data))

    test_tree_to_xml_with_io(tmp_path)
    path = tmp_path / "test.xml"
    with path.open("rb") as file:
        tree_from_xml(file)


def test_tree_to_binary_with_bytes() -> bytes:
    data = tree_to_binary(_test_tree())
    assert data is not None
    return data


def test_tree_to_binary_with_io(tmp_path):
    path = tmp_path / "test.tlv"
    with path.open("wb") as file:
        tree_to_binary(_test_tree(), file)


def test_tree_to_xml_with_bytes() -> bytes:
    data = tree_to_xml(_test_tree())
    assert data is not None
    return data


def test_tree_to_xml_with_io(tmp_path):
    path = tmp_path / "test.xml"
    with path.open("wb") as file:
        tree_to_xml(_test_tree(), file)


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
