from xml.etree import ElementTree

import pytest

from bertlv import config
from bertlv.tag import RootTag, Tag, TagClass, TagType


class TestTag:
    def test_init(self):
        tag = Tag(b"\x5F\x20")
        assert repr(tag) == "5f20"
        assert str(tag) == "0x5f20"

    def test_init_with_leading_zeros(self):
        tag = Tag(b"\x00\x00\x5F\x20")
        assert repr(tag) == "5f20"
        assert str(tag) == "0x5f20"

    def test_comparison(self):
        tag_5f20 = Tag(b"\x5F\x20")
        tag_5f20_2 = Tag(b"\x5F\x20")
        assert tag_5f20 == tag_5f20_2

        tag_5f21 = Tag(b"\x5F\x21")
        assert tag_5f20 < tag_5f21

    def test_init_with_empty_identifier(self):
        with pytest.raises(ValueError, match="tag must not be empty"):
            Tag(bytes())

    def test_init_with_missing_octets(self):
        with pytest.raises(ValueError, match="tag is missing subsequent octets: 5f$"):
            Tag(b"\x5F")

        with pytest.raises(ValueError, match="tag is missing subsequent octets: 5f81$"):
            Tag(b"\x5F\x81")

    def test_init_with_first_subsequent_octet_all_zero(self):
        Tag(b"\x5F\x80\x01")

        config.strict_checking = True
        with pytest.raises(
            ValueError,
            match="tag has first subsequent octet where bits 7 to 1 are all zero: 5f8001$",
        ):
            Tag(b"\x5F\x80\x01")
        config.strict_checking = False

    def test_init_with_invalid_subsequent(self):
        with pytest.raises(
            ValueError,
            match="tag has subsequent octet where bit 1 is not set: 5f6040$",
        ):
            Tag(b"\x5F\x60\x40")

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

        tag = Tag(bytes.fromhex("DF01"), force_constructed=True)
        assert tag.is_constructed()

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

    def test_from_int(self):
        tag = Tag.from_int(0x5F20)
        assert repr(tag) == "5f20"

    def test_from_hex(self):
        tag = Tag.from_hex("95")
        assert repr(tag) == "95"

        tag = Tag.from_hex("5F20")
        assert repr(tag) == "5f20"

    def test_from_hex_with_hex_prefix(self):
        tag = Tag.from_hex("0x5F20")
        assert repr(tag) == "5f20"

    def test_from_hex_with_leading_zeros(self):
        tag = Tag.from_hex("00005F20")
        assert repr(tag) == "5f20"

    def test_from_hex_with_invalid_tag(self):
        with pytest.raises(ValueError):
            Tag.from_hex("Invalid")


class TestRootTag:
    def test_init(self):
        tag = RootTag()
        assert repr(tag) == "root"
        assert str(tag) == "root"
