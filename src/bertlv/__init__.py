#!/usr/bin/env python3
"""
Library for BER TLV (tag-length-value) encoding.

Versioning scheme: https://semver.org/spec/v2.0.0.html
"""

from xml.etree import ElementTree

from .tree import Tree

__version__ = "0.1.0"
__author__ = "Philip Schömig"


def parse(data: bytes) -> Tree:
    return Tree.parse(data)


def from_xml(root: ElementTree.Element) -> Tree:
    return Tree.from_xml(root)
