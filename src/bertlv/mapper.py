from pathlib import Path
from typing import Iterable, List, Optional
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
                # TODO: verify value matches the type
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


_mappings: List[XmlMapping] = []


def init(mappings: Iterable[XmlMapping]):
    """Init the mappings list."""
    global _mappings
    _mappings = mappings


def parse(filenames: Iterable[Path]):
    """Parse the given mapping files."""
    global _mappings
    _mappings = [XmlMapping.parse(filename) for filename in filenames]


def reset():
    """Clear the stored mappings."""
    _mappings.clear()


def lookup(tag: str) -> Optional[ElementTree.Element]:
    """Look up the tag in the mappings and return the element.

    Returns None if the tag is not found.
    """
    for mapping in _mappings:
        element = mapping.lookup(tag)
        if element is not None:
            return element
    return None


def is_constructed(tag: str) -> Optional[bool]:
    """Look up the tag in the mappings and return True if it's constructed.

    Returns None if the tag is not found.
    """
    element = lookup(tag)
    if element is not None:
        return element.tag == "Element"
    return None


def encode(element: ElementTree.Element):
    """Encode the given element using the mappings."""
    for mapping in _mappings:
        if mapping.encode(element):
            break


def decode(element: ElementTree.Element):
    """Decode the given element using the mappings."""
    for mapping in _mappings:
        if mapping.decode(element):
            break


def encode_tree(root: ElementTree.Element):
    """Encode all elements in the given tree using the mappings."""
    for element in root:
        encode(element)
        encode_tree(element)


def decode_tree(root: ElementTree.Element):
    """Decode all elements in the given tree using the mappings."""
    for element in root:
        decode(element)
        decode_tree(element)
