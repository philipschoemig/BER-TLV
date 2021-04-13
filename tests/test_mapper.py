from xml.etree import ElementTree

import pytest

from bertlv import mapper
from bertlv.mapper import MapperError, XmlMapping


class TestXmlMapping:
    def test_init_with_wrong_element(self):
        with pytest.raises(
            MapperError,
            match=r"^expected root tag 'Mapping' or 'XMLMapping' but found 'Invalid'$",
        ):
            XmlMapping(ElementTree.Element("Invalid"))

    def test_lookup(self, tlv_xml_mapping):
        element = tlv_xml_mapping.lookup("0xDF0D")
        assert (
            ElementTree.tostring(element, encoding="unicode").strip()
            == """<Primitive TLVTag="0xDF0D" Type="String" XMLTag="PrimitiveTagDF0D" />"""
        )

        element = tlv_xml_mapping.lookup("0xdf0d")
        assert element is None

    def test_decode_primitive(self):
        map_root = ElementTree.fromstring(
            """<Mapping>
    <Primitive TLVTag="0xDF0D" Type="" XMLTag="PrimitiveTagDF0D" />
</Mapping>
"""
        )
        mapping = XmlMapping(map_root)
        element = ElementTree.Element("PrimitiveTagDF0D")

        mapping.decode(element)
        assert (
            ElementTree.tostring(element, encoding="unicode")
            == """<Primitive Tag="0xDF0D" Type="Hex" />"""
        )

    def test_decode_primitive_with_type_hex(self):
        map_root = ElementTree.fromstring(
            """<Mapping>
    <Primitive TLVTag="0xDF0D" Type="Hex" XMLTag="PrimitiveTagDF0D" />
</Mapping>
"""
        )
        mapping = XmlMapping(map_root)
        element = ElementTree.Element("PrimitiveTagDF0D")
        element.text = "0123"

        mapping.decode(element)
        assert (
            ElementTree.tostring(element, encoding="unicode")
            == """<Primitive Tag="0xDF0D" Type="Hex">0123</Primitive>"""
        )

    def test_decode_primitive_with_type_string(self):
        map_root = ElementTree.fromstring(
            """<Mapping>
    <Primitive TLVTag="0xDF0D" Type="String" XMLTag="PrimitiveTagDF0D" />
</Mapping>
"""
        )
        mapping = XmlMapping(map_root)
        element = ElementTree.Element("PrimitiveTagDF0D")
        element.text = "123 Go!"

        mapping.decode(element)
        assert (
            ElementTree.tostring(element, encoding="unicode")
            == """<Primitive Tag="0xDF0D" Type="ASCII">123 Go!</Primitive>"""
        )

    def test_decode_primitive_with_invalid_type(self):
        map_root = ElementTree.fromstring(
            """<Mapping>
    <Primitive TLVTag="0xDF0D" Type="" XMLTag="PrimitiveTagDF0D" />
</Mapping>
"""
        )
        mapping = XmlMapping(map_root)
        element = ElementTree.Element("PrimitiveTagDF0D")
        element.text = "123 Go!"

        with pytest.raises(
            MapperError,
            match=r"""^value is not hexadecimal as specified by mapping type '': """
            """element '<PrimitiveTagDF0D>123 Go!</PrimitiveTagDF0D>', """
            """mapping '<Primitive TLVTag="0xDF0D" Type="" XMLTag="PrimitiveTagDF0D" />'$""",
        ):
            mapping.decode(element)

    def test_decode_element(self):
        map_root = ElementTree.fromstring(
            """<Mapping>
    <Element TLVTag="0xE1" XMLTag="ConstructedTagE1" />
</Mapping>
"""
        )
        mapping = XmlMapping(map_root)
        element = ElementTree.Element("ConstructedTagE1")

        mapping.decode(element)
        assert (
            ElementTree.tostring(element, encoding="unicode")
            == """<Element Tag="0xE1" />"""
        )

    def test_encode_primitive(self):
        map_root = ElementTree.fromstring(
            """<Mapping>
    <Primitive TLVTag="0xDF0D" Type="" XMLTag="PrimitiveTagDF0D" />
</Mapping>
"""
        )
        mapping = XmlMapping(map_root)
        element = ElementTree.Element("Primitive", {"Tag": "0xDF0D", "Type": "Hex"})

        mapping.encode(element)
        assert (
            ElementTree.tostring(element, encoding="unicode")
            == """<PrimitiveTagDF0D />"""
        )

    def test_encode_primitive_with_type_hex(self):
        map_root = ElementTree.fromstring(
            """<Mapping>
    <Primitive TLVTag="0xDF0D" Type="Hex" XMLTag="PrimitiveTagDF0D" />
</Mapping>
"""
        )
        mapping = XmlMapping(map_root)
        element = ElementTree.Element("Primitive", {"Tag": "0xDF0D", "Type": "Hex"})
        element.text = "0123"

        mapping.encode(element)
        assert (
            ElementTree.tostring(element, encoding="unicode")
            == """<PrimitiveTagDF0D>0123</PrimitiveTagDF0D>"""
        )

    def test_encode_primitive_with_type_string(self):
        map_root = ElementTree.fromstring(
            """<Mapping>
    <Primitive TLVTag="0xDF0D" Type="String" XMLTag="PrimitiveTagDF0D" />
</Mapping>
"""
        )
        mapping = XmlMapping(map_root)
        element = ElementTree.Element("Primitive", {"Tag": "0xDF0D", "Type": "ASCII"})
        element.text = "123 Go!"

        mapping.encode(element)
        assert (
            ElementTree.tostring(element, encoding="unicode")
            == """<PrimitiveTagDF0D>123 Go!</PrimitiveTagDF0D>"""
        )

    def test_encode_primitive_with_type_mismatch(self):
        map_root = ElementTree.fromstring(
            """<Mapping>
    <Primitive TLVTag="0xDF0D" Type="String" XMLTag="PrimitiveTagDF0D" />
</Mapping>
"""
        )
        mapping = XmlMapping(map_root)
        element = ElementTree.Element("Primitive", {"Tag": "0xDF0D", "Type": "Hex"})
        element.text = "123 Go!"

        with pytest.raises(
            MapperError,
            match=r"""^mapping type 'String' doesn't match the actual type 'Hex': """
            """element '<Primitive Tag="0xDF0D" Type="Hex">123 Go!</Primitive>', """
            """mapping '<Primitive TLVTag="0xDF0D" Type="String" XMLTag="PrimitiveTagDF0D" />'$""",
        ):
            mapping.encode(element)

    def test_encode_primitive_with_invalid_type(self):
        map_root = ElementTree.fromstring(
            """<Mapping>
    <Primitive TLVTag="0xDF0D" Type="" XMLTag="PrimitiveTagDF0D" />
</Mapping>
"""
        )
        mapping = XmlMapping(map_root)
        element = ElementTree.Element("Primitive", {"Tag": "0xDF0D", "Type": "Hex"})
        element.text = "123 Go!"

        with pytest.raises(
            MapperError,
            match=r"""^value is not hexadecimal as specified by mapping type '': """
            """element '<Primitive Tag="0xDF0D" Type="Hex">123 Go!</Primitive>', """
            """mapping '<Primitive TLVTag="0xDF0D" Type="" XMLTag="PrimitiveTagDF0D" />'$""",
        ):
            mapping.encode(element)

    def test_encode_element(self):
        map_root = ElementTree.fromstring(
            """<Mapping>
    <Element TLVTag="0xE1" XMLTag="ConstructedTagE1" />
</Mapping>
"""
        )
        mapping = XmlMapping(map_root)
        element = ElementTree.Element("Element", {"Tag": "0xE1"})

        mapping.encode(element)
        assert (
            ElementTree.tostring(element, encoding="unicode")
            == """<ConstructedTagE1 />"""
        )

    def test_parse(self, tlv_file_mapping):
        mapping = XmlMapping.parse(tlv_file_mapping)
        assert mapping is not None

    def test_parse_with_wrong_element(self, tmp_path):
        string = b"""<?xml version="1.0" ?>
<Invalid />
"""
        path = tmp_path / "mapping_invalid.xml"
        path.write_bytes(string)
        with pytest.raises(
            MapperError,
            match=r"^error occurred while parsing the mapping file .*mapping_invalid.xml$",
        ):
            XmlMapping.parse(path)


def test_init(tlv_xml_mapping):
    mapper.init([tlv_xml_mapping])
    assert len(mapper._mappings) > 0


def test_parse(tlv_file_mapping):
    mapper.parse([tlv_file_mapping])
    assert len(mapper._mappings) > 0


def test_reset(tlv_file_mapping):
    mapper.reset()
    assert len(mapper._mappings) == 0


def test_lookup(tlv_xml_mapping):
    mapper.init([tlv_xml_mapping])
    element = mapper.lookup("0xDF0D")
    assert (
        ElementTree.tostring(element, encoding="unicode").strip()
        == """<Primitive TLVTag="0xDF0D" Type="String" XMLTag="PrimitiveTagDF0D" />"""
    )

    element = mapper.lookup("0xdf0d")
    assert element is None


def test_encode_tree(tlv_data_xml, tlv_string_xml_mapped, tlv_xml_mapping):
    mapper.init([tlv_xml_mapping])

    root = ElementTree.fromstring(tlv_data_xml)
    mapper.encode_tree(root)
    assert ElementTree.tostring(root, encoding="unicode") == tlv_string_xml_mapped


def test_decode_tree(tlv_data_xml_mapped, tlv_string_xml, tlv_xml_mapping):
    mapper.init([tlv_xml_mapping])

    root = ElementTree.fromstring(tlv_data_xml_mapped)
    mapper.decode_tree(root)
    assert ElementTree.tostring(root, encoding="unicode") == tlv_string_xml


def test_encode_tree_with_multiple_mappings(tlv_data_xml, tlv_xml_mapping):
    map_root = ElementTree.fromstring(
        """<Mapping>
  <Element TLVTag="0xE1" XMLTag="ConstructedTagE1Test"/>
  <Primitive TLVTag="0x9F1E" Type="" XMLTag="PrimitiveTag9F1ETest"/>
</Mapping>
"""
    )
    mapper.init([XmlMapping(map_root), tlv_xml_mapping])

    root = ElementTree.fromstring(tlv_data_xml)
    mapper.encode_tree(root)
    assert (
        ElementTree.tostring(root, encoding="unicode")
        == """<Tlv>
  <ConstructedTagE1Test>
    <PrimitiveTag9F1ETest>16021437</PrimitiveTag9F1ETest>
    <ConstructedTagEF>
      <PrimitiveTagDF0D>M000-MPI</PrimitiveTagDF0D>
      <PrimitiveTagDF7F>1-22</PrimitiveTagDF7F>
    </ConstructedTagEF>
    <ConstructedTagEF>
      <PrimitiveTagDF0D>M000-TESTOS</PrimitiveTagDF0D>
      <PrimitiveTagDF7F>6-5</PrimitiveTagDF7F>
    </ConstructedTagEF>
  </ConstructedTagE1Test>
</Tlv>"""
    )

    mapper.decode_tree(root)
    assert (
        ElementTree.tostring(root, encoding="unicode")
        == """<Tlv>
  <Element Tag="0xE1">
    <Primitive Tag="0x9F1E" Type="Hex">16021437</Primitive>
    <Element Tag="0xEF">
      <Primitive Tag="0xDF0D" Type="ASCII">M000-MPI</Primitive>
      <Primitive Tag="0xDF7F" Type="ASCII">1-22</Primitive>
    </Element>
    <Element Tag="0xEF">
      <Primitive Tag="0xDF0D" Type="ASCII">M000-TESTOS</Primitive>
      <Primitive Tag="0xDF7F" Type="ASCII">6-5</Primitive>
    </Element>
  </Element>
</Tlv>"""
    )
