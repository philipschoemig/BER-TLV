from xml.etree import ElementTree

from bertlv.mapper import XmlMapper, XmlMapping


class TestXmlMapping:
    def test_process_primitive(self):
        map_root = ElementTree.fromstring(
            """<Mapping>
    <Primitive TLVTag="0xDF0D" Type="" XMLTag="PrimitiveTagDF0D"/>
</Mapping>
"""
        )
        mapping = XmlMapping(map_root)
        element = ElementTree.Element("Primitive", {"Tag": "0xDF0D", "Type": "Hex"})

        mapping.process(element)
        assert (
            ElementTree.tostring(element, encoding="unicode")
            == """<PrimitiveTagDF0D />"""
        )

        mapping.process(element)
        assert (
            ElementTree.tostring(element, encoding="unicode")
            == """<Primitive Tag="0xDF0D" Type="Hex" />"""
        )

    def test_process_primitive_with_type(self):
        map_root = ElementTree.fromstring(
            """<Mapping>
    <Primitive TLVTag="0xDF0D" Type="String" XMLTag="PrimitiveTagDF0D"/>
</Mapping>
"""
        )
        mapping = XmlMapping(map_root)
        element = ElementTree.Element("Primitive", {"Tag": "0xDF0D", "Type": "Hex"})

        mapping.process(element)
        assert (
            ElementTree.tostring(element, encoding="unicode")
            == """<PrimitiveTagDF0D />"""
        )

        mapping.process(element)
        assert (
            ElementTree.tostring(element, encoding="unicode")
            == """<Primitive Tag="0xDF0D" Type="ASCII" />"""
        )

    def test_process_element(self):
        map_root = ElementTree.fromstring(
            """<Mapping>
    <Element TLVTag="0xE1" XMLTag="ConstructedTagE1"/>
</Mapping>
"""
        )
        mapping = XmlMapping(map_root)
        element = ElementTree.Element("Element", {"Tag": "0xE1"})

        mapping.process(element)
        assert (
            ElementTree.tostring(element, encoding="unicode")
            == """<ConstructedTagE1 />"""
        )

        mapping.process(element)
        assert (
            ElementTree.tostring(element, encoding="unicode")
            == """<Element Tag="0xE1" />"""
        )


class TestXmlMapper:
    def test_map(self, tlv_data_xml, tlv_xml_mapping):
        mappings = [tlv_xml_mapping]
        mapper = XmlMapper(mappings)
        root = ElementTree.fromstring(tlv_data_xml)

        mapper.map(root)
        assert (
            ElementTree.tostring(root, encoding="unicode")
            == """<Tlv>
  <ConstructedTagE1>
    <PrimitiveTag9F1E>16021437</PrimitiveTag9F1E>
    <ConstructedTagEF>
      <PrimitiveTagDF0D>M000-MPI</PrimitiveTagDF0D>
      <PrimitiveTagDF7F>1-22</PrimitiveTagDF7F>
    </ConstructedTagEF>
    <ConstructedTagEF>
      <PrimitiveTagDF0D>M000-TESTOS</PrimitiveTagDF0D>
      <PrimitiveTagDF7F>6-5</PrimitiveTagDF7F>
    </ConstructedTagEF>
  </ConstructedTagE1>
</Tlv>"""
        )

        mapper.map(root)
        assert (
            ElementTree.tostring(root, encoding="unicode")
            == """<Tlv>
  <Element Tag="0xE1">
    <Primitive Tag="0x9F1E" Type="ASCII">16021437</Primitive>
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

    def test_map_with_multiple_mappings(self, tlv_data_xml, tlv_xml_mapping):
        map_root = ElementTree.fromstring(
            """<Mapping>
    <Element TLVTag="0xE1" XMLTag="ConstructedTagE1Test"/>
    <Primitive TLVTag="0x9F1E" Type="" XMLTag="PrimitiveTag9F1ETest"/>
</Mapping>
"""
        )
        mappings = [XmlMapping(map_root), tlv_xml_mapping]
        mapper = XmlMapper(mappings)
        root = ElementTree.fromstring(tlv_data_xml)
        mapper.map(root)
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

        mapper.map(root)
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
