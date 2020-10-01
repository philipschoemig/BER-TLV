import io

from bertlv.generator import BinaryGenerator, XmlGenerator, generate, generate_bytes
from bertlv.tag import Tag
from bertlv.tree import TlvNode


class TestBinaryGenerator:
    def test_close(self):
        children = [TlvNode(Tag.from_hex("5F20"), b"\x11\x22\x33")]
        node = TlvNode(Tag.from_hex("FF60"), children=children)
        generator = BinaryGenerator()
        generator.write(node)
        data = generator.close()
        assert data == b"\xFF\x60\x06\x5F\x20\x03\x11\x22\x33"

    def test_close_with_zero_length(self):
        children = [TlvNode(Tag.from_hex("5F20"))]
        node = TlvNode(Tag.from_hex("FF60"), children=children)
        generator = BinaryGenerator()
        generator.write(node)
        data = generator.close()
        assert data == b"\xFF\x60\x03\x5F\x20\x00"

    def test_close_with_extended_length(self):
        value = bytes([i for i in range(1, 256)])
        children = [TlvNode(Tag.from_hex("5F20"), value)]
        node = TlvNode(Tag.from_hex("FF60"), children=children)
        generator = BinaryGenerator()
        generator.write(node)
        data = generator.close()
        assert data == b"\xFF\x60\x82\x01\x03\x5F\x20\x81\xff" + value


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

    def test_close_with_wrong_encoding(self):
        node = TlvNode(Tag.from_hex("5F20"), b"\x00\x7F\xFF")
        generator = XmlGenerator()
        generator.write(node)
        data = generator.close()
        # Convert OS line endings to newline for comparison
        data = b"\n".join(data.splitlines())
        assert (
            data
            == b"""<?xml version="1.0" ?>
<Tlv>
  <Primitive Tag="0x5F20" Type="Hex">007FFF</Primitive>
</Tlv>"""
        )


def test_generate(tlv_binary_data, tlv_tree):
    fp = io.BytesIO()
    generate(fp, tlv_tree, BinaryGenerator())
    assert fp.getvalue() == tlv_binary_data


def test_generate_bytes(tlv_binary_data, tlv_tree):
    data = generate_bytes(tlv_tree, BinaryGenerator())
    assert data == tlv_binary_data
