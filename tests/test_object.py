from xml.etree import ElementTree

import pytest

from bertlv.object import Element, Primitive
from bertlv.stream import Stream
from bertlv.tag import Tag


class TestElement:
    def test_init(self):
        element = Element(Tag.from_hex("FF60"))
        assert str(element) == "Element 0xff60: []"

        with pytest.raises(
            RuntimeError,
            match="Element class expects a constructed TLV tag, "
            "but got a primitive tag: 0x5f20",
        ):
            Element(Tag.from_hex("5F20"))

    def test_length(self):
        element = Element(Tag.from_hex("FF60"))
        assert element.length == 0

    def test_find(self):
        children = [Primitive(Tag.from_hex("5F20"), bytes.fromhex("112233"))]
        element = Element(Tag.from_hex("FF60"), children)
        assert element.find("5F20") is children[0]

    def test_build(self):
        children = [Primitive(Tag.from_hex("5F20"), bytes.fromhex("112233"))]
        element = Element(Tag.from_hex("FF60"), children)
        assert element.build().hex() == "ff60065f2003112233"

    def test_to_xml(self):
        parent = ElementTree.Element("Element", {"Tag": "0xE0"})
        children = [Primitive(Tag.from_hex("5F20"), bytes.fromhex("112233"))]
        element = Element(Tag.from_hex("FF60"), children)
        assert (
            ElementTree.tostring(element.to_xml(parent)) == b'<Element Tag="0xFF60">'
            b'<Primitive Tag="0x5F20" Type="Hex">112233</Primitive></Element>'
        )

    def test_dump(self):
        children = [Primitive(Tag.from_hex("5F20"), bytes.fromhex("112233"))]
        element = Element(Tag.from_hex("FF60"), children)
        assert element.dump("  ", 0) == "0xff60\n  0x5f20: 112233\n"

    def test_parse(self):
        tlv = Stream(bytes.fromhex("FF60065F2003112233"))
        element = Element.parse(tlv)
        assert str(element) == "Element 0xff60: [Primitive 0x5f20: 112233]"

    def test_from_xml(self):
        xml = ElementTree.fromstring(
            b'<Element Tag="0xFF60">'
            b'<Primitive Tag="0x5F20" Type="Hex">112233</Primitive></Element>'
        )
        element = Element.from_xml(xml)
        assert str(element) == "Element 0xff60: [Primitive 0x5f20: 112233]"

    def test_from_xml_with_empty_element(self):
        xml = ElementTree.fromstring(b'<Element Tag="0xFF60"/>')
        element = Element.from_xml(xml)
        assert str(element) == "Element 0xff60: []"


class TestPrimitive:
    def test_init(self):
        primitive = Primitive(Tag.from_hex("5F20"), bytes.fromhex("112233"))
        assert str(primitive) == "Primitive 0x5f20: 112233"

        with pytest.raises(
            RuntimeError,
            match="Primitive class expects a primitive TLV tag, "
            "but got a constructed tag: 0xff60",
        ):
            Primitive(Tag.from_hex("FF60"), bytes())

    def test_str(self):
        primitive = Primitive(Tag.from_hex("5F20"), bytes())
        assert str(primitive) == "Primitive 0x5f20: Empty"

    def test_length(self):
        primitive = Primitive(Tag.from_hex("5F20"), bytes())
        assert primitive.length == 0

        primitive = Primitive(Tag.from_hex("5F20"), bytes.fromhex("112233"))
        assert primitive.length == 3

    def test_find(self):
        primitive = Primitive(Tag.from_hex("5F20"), bytes.fromhex("112233"))
        assert primitive.find("5F20") is None

    def test_build(self):
        primitive = Primitive(Tag.from_hex("5F20"), bytes.fromhex("112233"))
        assert primitive.build().hex() == "5f2003112233"

    def test_to_xml(self):
        parent = ElementTree.Element("Element", {"Tag": "0xE0"})
        primitive = Primitive(Tag.from_hex("5F20"), bytes.fromhex("112233"))
        assert (
            ElementTree.tostring(primitive.to_xml(parent))
            == b'<Primitive Tag="0x5F20" Type="Hex">112233</Primitive>'  # noqa: W503
        )

    def test_dump(self):
        primitive = Primitive(Tag.from_hex("5F20"), bytes.fromhex("112233"))
        assert primitive.dump("  ", 0) == "0x5f20: 112233\n"

    def test_parse(self):
        tlv = Stream(bytes.fromhex("5F2003112233"))
        primitive = Primitive.parse(tlv)
        assert str(primitive) == "Primitive 0x5f20: 112233"

    def test_from_xml(self):
        xml = ElementTree.fromstring(
            b'<Primitive Tag="0x5F20" Type="Hex">112233</Primitive>'
        )
        primitive = Primitive.from_xml(xml)
        assert str(primitive) == "Primitive 0x5f20: 112233"

    def test_from_xml_with_empty_primitive(self):
        xml = ElementTree.fromstring(b'<Primitive Tag="0x5F20" Type="Hex"/>')
        primitive = Primitive.from_xml(xml)
        assert str(primitive) == "Primitive 0x5f20: Empty"
