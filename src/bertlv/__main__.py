#!/usr/bin/env python3
"""Module allowing for ``python -m bertlv ...``."""
import argparse
import os
import sys

from . import (
    __version__,
    config,
    tree_from_binary,
    tree_from_xml,
    tree_to_binary,
    tree_to_xml,
)


def main(argv=None) -> int:
    """Main function for the bertlv module.

    Parse the input file specified on the command line and dump the resulting TLV tree
    to standard output or the optional output file.
    """
    # noinspection PyTypeChecker
    parser = argparse.ArgumentParser(
        description="BER TLV parser.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-V", "--version", action="version", version=__version__)
    parser.add_argument(
        "-s",
        "--strict",
        action="store_true",
        help="Enable strict checking of TLV encoding",
    )
    parser.add_argument("-o", "--output", help="Path to the output file")
    parser.add_argument(
        "file", metavar="FILE", help="Path to the file containing a TLV tree"
    )

    args = parser.parse_args(argv)

    config.strict_checking = args.strict

    with open(args.file, "rb") as file:
        _, ext = os.path.splitext(args.file)
        if ext == ".xml":
            tlv_tree = tree_from_xml(file)
        elif ext == ".tlv":
            tlv_tree = tree_from_binary(file)
        else:
            print(f"Unknown file extension '{ext}' for input file: {args.file}")
            return 1

    dump = tlv_tree.dump()
    if args.output:
        with open(args.output, "wb") as file:
            _, ext = os.path.splitext(args.output)
            if ext == ".xml":
                tree_to_xml(tlv_tree, file)
            elif ext == ".tlv":
                tree_to_binary(tlv_tree, file)
            elif ext == ".txt":
                file.write(dump.encode("utf-8"))
            else:
                print(f"Unknown file extension '{ext}' for output file: {args.output}")
                return 1
    else:
        print(dump)

    return 0


if __name__ == "__main__":
    # Execute the following lines only when this script is called directly.
    # When it is included from another script they are ignored.
    sys.exit(main())
