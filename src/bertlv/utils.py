"""Module containing utility functions"""
import os
import re
import xml.dom.minidom

from dataclasses import asdict, dataclass
from xml.etree import ElementTree


@dataclass
class XmlSettings:
    """XML settings as expected by the method :obj:`~xml.dom.minidom.Node.toprettyxml()`."""

    indent: str = "  "
    """Specifies the indentation string."""
    newl: str = os.linesep
    """Specifies the string emitted at the end of each line."""
    encoding: str = "utf-8"
    """Specifies the encoding to use for the output."""


XML_SETTINGS_DEFAULT = XmlSettings()


def xml_prettify(string: str, settings: XmlSettings = XML_SETTINGS_DEFAULT) -> bytes:
    """Return a pretty-printed XML byte-string for the raw XML string. """
    # Remove whitespace between XML elements
    string = re.sub(r">\s+<", "><", string)
    document = xml.dom.minidom.parseString(string)
    return document.toprettyxml(**asdict(settings))


def xml_prettify_element(
    element: ElementTree.Element, settings: XmlSettings = XML_SETTINGS_DEFAULT
) -> bytes:
    """Return a pretty-printed XML byte-string for the element. """
    string = ElementTree.tostring(element, settings.encoding).decode(settings.encoding)
    return xml_prettify(string, settings)
