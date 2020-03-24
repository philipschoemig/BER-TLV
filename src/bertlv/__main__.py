#!/usr/bin/env python3
"""Module allowing for ``python -m bertlv ...``."""
import argparse
import sys
from xml.dom import minidom
from xml.etree import ElementTree

from . import parse, __version__


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="BER TLV parser.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--version", "-V", action="version", version=__version__)
    parser.add_argument("file", metavar="FILE", help="Path to the TLV file")

    args = parser.parse_args(argv)

    with open(args.file, "rb") as file:
        data = file.read()
    tlv_tree = parse(data)
    print(tlv_tree.dump("\t"))

    xmlstr = minidom.parseString(ElementTree.tostring(tlv_tree.to_xml())).toprettyxml(
        indent="  "
    )
    print(xmlstr)
    return 0


if __name__ == "__main__":
    # Execute the following lines only when this script is called directly.
    # When it is included from another script they are ignored.
    status = main()
    sys.exit(status)
