import io

from bertlv.generator import BinaryGenerator, XmlGenerator, generate, generate_bytes
from bertlv.tag import Tag
from bertlv.tree import TlvNode, Tree


class TestBinaryGenerator:
    def test_close(self):
        children = [TlvNode(Tag.from_hex("5F20"), b"\x11\x22\x33")]
        node = TlvNode(Tag.from_hex("FF60"), children=children)
        generator = BinaryGenerator()
        generator.write(node)
        data = generator.close()
        assert data == b"\xFF\x60\x06\x5F\x20\x03\x11\x22\x33"


class TestXmlGenerator:
    def test_close(self):
        children = [TlvNode(Tag.from_hex("5F20"), b"\x11\x22\x33")]
        node = TlvNode(Tag.from_hex("FF60"), children=children)
        generator = XmlGenerator()
        generator.write(node)
        data = generator.close()
        # Convert OS line endings to newline for comparison
        data = b"\n".join(data.splitlines())
        assert (
            data
            == b"""<?xml version="1.0" ?>
<Tlv>
  <Element Tag="0xFF60">
    <Primitive Tag="0x5F20" Type="Hex">112233</Primitive>
  </Element>
</Tlv>"""
        )

    def test_close_with_type_ascii(self):
        node = TlvNode(Tag.from_hex("5F20"), b"\x31\x32\x33")
        generator = XmlGenerator()
        generator.write(node)
        data = generator.close()
        # Convert OS line endings to newline for comparison
        data = b"\n".join(data.splitlines())
        assert (
            data
            == b"""<?xml version="1.0" ?>
<Tlv>
  <Primitive Tag="0x5F20" Type="ASCII">123</Primitive>
</Tlv>"""
        )


def test_generate():
    fp = io.BytesIO()
    generate(fp, _test_tree(), BinaryGenerator())
    assert fp.getvalue() == _test_data()


def test_generate_bytes():
    data = generate_bytes(_test_tree(), BinaryGenerator())
    assert data == _test_data()


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


def _test_data():
    """Return the data for the test tree."""
    return (
        b"\xe1\x35\x9f\x1e\x08\x31\x36\x30\x32\x31\x34\x33\x37\xef\x12\xdf"
        b"\x0d\x08\x4d\x30\x30\x30\x2d\x4d\x50\x49\xdf\x7f\x04\x31\x2d\x32"
        b"\x32\xef\x14\xdf\x0d\x0b\x4d\x30\x30\x30\x2d\x54\x45\x53\x54\x4f"
        b"\x53\xdf\x7f\x03\x36\x2d\x35"
    )
