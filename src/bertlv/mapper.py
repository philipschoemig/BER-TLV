from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree


class XmlMapping:
    def __init__(self, root: ElementTree.Element):
        if root.tag != "Mapping" and root.tag != "XMLMapping":
            raise ValueError(
                f"Expected root tag 'Mapping' or 'XMLMapping' but found {root.tag}"
            )
        self.root = root

    def process(self, element: ElementTree.Element) -> bool:
        """Process the mapping for the given element."""
        processed = False
        if element.tag == "Element" or element.tag == "Primitive":
            map_entry = self.root.find(
                f"./{element.tag}[@TLVTag='{element.get('Tag')}']"
            )
            if map_entry is not None:
                tag = map_entry.get("XMLTag")
                element.tag = tag
                element.attrib.clear()
                processed = True
        else:
            map_entry = self.root.find(f"./*[@XMLTag='{element.tag}']")
            if map_entry is not None:
                element.tag = map_entry.tag
                element.attrib.clear()

                attrib_tag = map_entry.get("TLVTag")
                element.set("Tag", attrib_tag)

                if map_entry.tag == "Primitive":
                    attrib_type = "Hex"
                    if map_entry.get("Type") == "String":
                        attrib_type = "ASCII"
                    element.set("Type", attrib_type)
                processed = True
        return processed

    @classmethod
    def parse(cls, filename: Path) -> "XmlMapping":
        """Parse the given mapping file."""
        tree = ElementTree.parse(filename)
        root = tree.getroot()
        try:
            obj = cls(root)
        except ValueError as e:
            raise ValueError(
                f"Error occurred while parsing the mapping file {filename}"
            ) from e
        return obj


class XmlMapper:
    def __init__(self, mappings: Iterable[XmlMapping]):
        self.mappings = mappings

    def map(self, root: ElementTree.Element):
        """Map all elements in the given tree using the stored mappings."""
        for element in root:
            self.map(element)
            for mapping in self.mappings:
                if mapping.process(element):
                    break

    @classmethod
    def parse(cls, filenames: Iterable[Path]) -> "XmlMapper":
        """Parse the given mapping files."""
        mappings = [XmlMapping.parse(filename) for filename in filenames]
        return cls(mappings)
