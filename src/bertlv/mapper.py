from pathlib import Path
from typing import Iterable, Optional
from xml.etree import ElementTree


class XmlMapping:
    def __init__(self, root: ElementTree.Element):
        if root.tag != "Mapping" and root.tag != "XMLMapping":
            raise ValueError(
                f"Expected root tag 'Mapping' or 'XMLMapping' but found {root.tag}"
            )
        self.root = root

    def lookup(self, tag: str) -> Optional[ElementTree.Element]:
        """Look up the tag in the mapping and return the element."""
        return self.root.find(f"./*[@TLVTag='{tag}']")

    def decode(self, element: ElementTree.Element) -> bool:
        """Process the mapping for the given element."""
        processed = False
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

    def encode(self, element: ElementTree.Element) -> bool:
        """Process the mapping for the given element."""
        processed = False
        map_entry = self.root.find(f"./{element.tag}[@TLVTag='{element.get('Tag')}']")
        if map_entry is not None:
            tag = map_entry.get("XMLTag")
            element.tag = tag
            element.attrib.clear()
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


class Mapper:
    def __init__(self, mappings: Iterable[XmlMapping]):
        self.mappings = mappings

    def lookup(self, tag: str) -> Optional[ElementTree.Element]:
        """Look up the tag in the mappings and return the element."""
        for mapping in self.mappings:
            element = mapping.lookup(tag)
            if element is not None:
                return element
        return None

    def map(self, element: ElementTree.Element):
        """Map the given element using the mappings."""
        for mapping in self.mappings:
            if mapping.encode(element):
                break

    def unmap(self, element: ElementTree.Element):
        """Unmap the given element using the mappings."""
        for mapping in self.mappings:
            if mapping.decode(element):
                break

    def map_tree(self, root: ElementTree.Element):
        """Map all elements in the given tree using the mappings."""
        for element in root:
            self.map(element)
            self.map_tree(element)

    def unmap_tree(self, root: ElementTree.Element):
        """Unmap all elements in the given tree using the mappings."""
        for element in root:
            self.unmap(element)
            self.unmap_tree(element)

    @classmethod
    def parse(cls, filenames: Iterable[Path]) -> "Mapper":
        """Parse the given mapping files."""
        mappings = [XmlMapping.parse(filename) for filename in filenames]
        return cls(mappings)
