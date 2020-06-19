from bertlv.generator import BinaryGenerator, XmlGenerator
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
