from xml.etree import ElementTree

import pytest

from bertlv.stream import Stream
from bertlv.tag import Tag, TagClass, TagType


class TestTag:
    def test_init(self):
        tag = Tag(bytes.fromhex("5F20"))
        assert repr(tag) == "5f20"

    def test_repr(self):
        tag = Tag(bytes.fromhex("5F20"))
        assert repr(tag) == "5f20"

    def test_str(self):
        tag = Tag(bytes.fromhex("5F20"))
        assert str(tag) == "0x5f20"

    def test_tag_class(self):
        tag = Tag(bytes.fromhex("1F01"))
        assert tag.tag_class == TagClass.UNIVERSAL

        tag = Tag(bytes.fromhex("5F20"))
        assert tag.tag_class == TagClass.APPLICATION

        tag = Tag(bytes.fromhex("9F01"))
        assert tag.tag_class == TagClass.CONTEXT_SPECIFIC

        tag = Tag(bytes.fromhex("DF01"))
        assert tag.tag_class == TagClass.PRIVATE

    def test_tag_type(self):
        tag = Tag(bytes.fromhex("DF01"))
        assert tag.tag_type == TagType.PRIMITIVE

        tag = Tag(bytes.fromhex("FF60"))
        assert tag.tag_type == TagType.CONSTRUCTED

    def test_is_constructed(self):
        tag = Tag(bytes.fromhex("DF01"))
        assert not tag.is_constructed()

        tag = Tag(bytes.fromhex("FF60"))
        assert tag.is_constructed()

    def test_build(self):
        tag = Tag(bytes.fromhex("5f20"))
        assert tag.build().hex() == "5f20"

    def test_to_int(self):
        tag = Tag(bytes.fromhex("5f20"))
        assert tag.to_int() == 24352

    def test_to_hex(self):
        tag = Tag(bytes.fromhex("5f20"))
        assert tag.to_hex() == "0x5F20"

    def test_to_xml(self):
        tag = Tag(bytes.fromhex("5f20"))
        element = ElementTree.Element("Primitive")
        assert tag.to_xml(element).get("Tag") == tag.to_hex()

    def test_parse(self):
        tlv = Stream(bytes.fromhex("5F20"))
        tag = Tag.parse(tlv)
        assert repr(tag) == "5f20"

    def test_from_int(self):
        tag = Tag.from_int(0x5F20)
        assert repr(tag) == "5f20"

    def test_from_hex(self):
        tag = Tag.from_hex("5F20")
        assert repr(tag) == "5f20"

        tag = Tag.from_hex("0x00005F20")
        assert repr(tag) == "5f20"

    def test_from_hex_with_invalid_tag(self):
        with pytest.raises(ValueError):
            Tag.from_hex("Invalid")

    def test_from_xml(self):
        element = ElementTree.Element("Primitive", {"Tag": "0x5F20"})
        tag = Tag.from_xml(element)
        assert repr(tag) == "5f20"

        element = ElementTree.Element("Element", {"Tag": "0x5F20"})
        tag = Tag.from_xml(element)
        assert repr(tag) == "5f20"

    def test_from_xml_with_missing_tag(self):
        element = ElementTree.Element("Test")
        with pytest.raises(RuntimeError, match="Element is missing 'Tag' attribute"):
            Tag.from_xml(element)

    def test_from_xml_with_invalid_tag(self):
        element = ElementTree.Element("Primitive", {"Tag": "Invalid"})
        with pytest.raises(RuntimeError, match="Invalid Tag"):
            Tag.from_xml(element)
