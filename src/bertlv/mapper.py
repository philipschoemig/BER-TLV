from pathlib import Path
from typing import Iterable, List, Optional
from xml.etree import ElementTree

from bertlv import utils
from bertlv.tree import TlvError


class MapperError(TlvError):
    def __init__(
        self,
        message: str,
        *,
        element: ElementTree.Element = None,
        mapping: ElementTree.Element = None,
    ):
        kwargs = {}
        if element is not None:
            string = ElementTree.tostring(element, encoding="unicode")
            kwargs["element"] = f"'{string.rstrip()}'"
        if mapping is not None:
            string = ElementTree.tostring(mapping, encoding="unicode")
            kwargs["mapping"] = f"'{string.rstrip()}'"
        super().__init__(f"{message}", **kwargs)


class XmlMapping:
    TYPE_MAP = {
        "String": "ASCII",
        "Hex": "Hex",
        "": "Hex",
    }

    def __init__(self, root: ElementTree.Element):
        if root.tag != "Mapping" and root.tag != "XMLMapping":
            raise MapperError(
                f"expected root tag 'Mapping' or 'XMLMapping' but found '{root.tag}'"
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
            self._check_type(map_entry, element)
            element.tag = map_entry.tag
            element.attrib.clear()
            element.set("Tag", map_entry.get("TLVTag"))
            if map_entry.tag == "Primitive":
                element.set("Type", self.TYPE_MAP[map_entry.get("Type")])
            processed = True
        return processed

    def encode(self, element: ElementTree.Element) -> bool:
        """Process the mapping for the given element."""
        processed = False
        map_entry = self.root.find(f"./{element.tag}[@TLVTag='{element.get('Tag')}']")
        if map_entry is not None:
            self._check_type(map_entry, element)
            element.tag = map_entry.get("XMLTag")
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
        except MapperError as e:
            raise MapperError(
                f"error occurred while parsing the mapping file {filename}"
            ) from e
        return obj

    def _check_type(self, map_entry: ElementTree.Element, element: ElementTree.Element):
        if map_entry.tag == "Primitive":
            map_type = map_entry.get("Type")
            actual_type = element.get("Type")
            if map_type and actual_type and actual_type != self.TYPE_MAP[map_type]:
                raise MapperError(
                    f"mapping type '{map_type}' doesn't match the actual type '{actual_type}'",
                    element=element,
                    mapping=map_entry,
                )
            if element.text:
                if self.TYPE_MAP[map_type] == "Hex":
                    try:
                        utils.xml_text2hex(element)
                    except ValueError as e:
                        raise MapperError(
                            f"value is not hexadecimal as specified by mapping type '{map_entry.get('Type')}'",
                            element=element,
                            mapping=map_entry,
                        ) from e


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
