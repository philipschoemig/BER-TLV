#!/usr/bin/env python3
"""
Python library for BER-TLV en-/decoding.

Versioning scheme: https://semver.org/spec/v2.0.0.html
"""
import io
from typing import BinaryIO, Union, Optional

from . import generator, parser
from .tree import Tree

__version__ = "0.2.3"
__author__ = "Philip Schömig"


def tree_from_binary(source: Union[bytes, BinaryIO]) -> Tree:
    """Parse a TLV tree from binary data. Return the resulting `Tree`.

    *source* is either a bytes-like object or an open binary file object.
    """
    parser_instance = parser.BinaryParser()
    if isinstance(source, bytes):
        return parser.parse_bytes(source, parser_instance)
    if isinstance(source, (BinaryIO, io.BufferedIOBase)):
        return parser.parse(source, parser_instance)
    raise TypeError(
        f"source must be a bytes or BinaryIO object but is '{type(source)}'"
    )


def tree_from_xml(source: Union[bytes, BinaryIO]) -> Tree:
    """Parse a TLV tree from XML data. Return the resulting `Tree`.

    *source* is either a bytes-like object or an open binary file object.
    """
    parser_instance = parser.XmlParser()
    if isinstance(source, bytes):
        return parser.parse_bytes(source, parser_instance)
    if isinstance(source, (BinaryIO, io.BufferedIOBase)):
        return parser.parse(source, parser_instance)
    raise TypeError(
        f"source must be a bytes or BinaryIO object but is '{type(source)}'"
    )


def tree_to_binary(source: Tree, file: BinaryIO = None) -> Optional[bytes]:
    """Generate binary data of a TLV tree.
    Return the resulting `bytes` only if *file* is ``None`` otherwise write data to *file*.

    *source* is a `Tree` object.
    *file* is an open binary file object.
    """
    generator_instance = generator.BinaryGenerator()
    if file:
        generator.generate(file, source, generator_instance)
        return None
    return generator.generate_bytes(source, generator_instance)


def tree_to_xml(source: Tree, file: BinaryIO = None) -> Optional[bytes]:
    """Generate XML data of a TLV tree.
    Return the resulting `bytes` only if *file* is ``None`` otherwise write data to *file*.

    *source* is a `Tree` object.
    *file* is an open binary file object.
    """
    generator_instance = generator.XmlGenerator()
    if file:
        generator.generate(file, source, generator_instance)
        return None
    return generator.generate_bytes(source, generator_instance)
