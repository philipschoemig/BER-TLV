#!/usr/bin/env python3
"""
Python library for BER-TLV en-/decoding.

Versioning scheme: https://semver.org/spec/v2.0.0.html
"""
from typing import BinaryIO, Optional, Union

from . import generator, parser
from .tree import Tree

__version__ = "0.2.4"
__author__ = "Philip Schömig"


def tree_from_binary(source: Union[bytes, BinaryIO]) -> Tree:
    """Parse a TLV tree from binary data and return the resulting `Tree`."""
    parser_instance = parser.BinaryParser()
    try:
        return parser.parse_bytes(source, parser_instance)
    except TypeError:
        return parser.parse(source, parser_instance)


def tree_from_xml(source: Union[bytes, BinaryIO]) -> Tree:
    """Parse a TLV tree from XML data and return the resulting `Tree`."""
    parser_instance = parser.XmlParser()
    try:
        return parser.parse_bytes(source, parser_instance)
    except TypeError:
        return parser.parse(source, parser_instance)


def tree_to_binary(source: Tree, file: BinaryIO = None) -> Optional[bytes]:
    """Generate binary data of a TLV tree and return it or write it to *file*.

    If *file* is ``None`` return the `bytes` otherwise write data to *file*.
    """
    generator_instance = generator.BinaryGenerator()
    if file:
        generator.generate(file, source, generator_instance)
        return None
    return generator.generate_bytes(source, generator_instance)


def tree_to_xml(source: Tree, file: BinaryIO = None) -> Optional[bytes]:
    """Generate XML data of a TLV tree and return it or write it to *file*.

    If *file* is ``None`` return the `bytes` otherwise write data to *file*.
    """
    generator_instance = generator.XmlGenerator()
    if file:
        generator.generate(file, source, generator_instance)
        return None
    return generator.generate_bytes(source, generator_instance)
