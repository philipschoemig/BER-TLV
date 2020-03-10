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
            match="Element class expects a constructed TLV tag, but got a primitive tag: 0x5f20",
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
            ElementTree.tostring(element.to_xml(parent))
            == b'<Element Tag="0xFF60"><Primitive Tag="0x5F20" Type="Hex">112233</Primitive></Element>'
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
            b'<Element Tag="0xFF60"><Primitive Tag="0x5F20" Type="Hex">112233</Primitive></Element>'
        )
        element = Element.from_xml(xml)
        assert str(element) == "Element 0xff60: [Primitive 0x5f20: 112233]"
