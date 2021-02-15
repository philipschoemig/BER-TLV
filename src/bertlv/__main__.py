#!/usr/bin/env python3
"""Module allowing for ``python -m bertlv ...``."""
import argparse
import contextlib
import sys

from pathlib import Path
from typing import List

from . import (
    __version__,
    config,
    mapper,
    tree_from_binary,
    tree_from_xml,
    tree_to_binary,
    tree_to_text,
    tree_to_xml,
)

INPUT_FORMATS = {
    "tlv": tree_from_binary,
    "xml": tree_from_xml,
}
OUTPUT_FORMATS = {
    "tlv": tree_to_binary,
    "txt": tree_to_text,
    "xml": tree_to_xml,
}


def detect_file_format(filename: str, formats: dict, default: str = None) -> str:
    if filename == "-" and default is not None:
        return default
    file_format = Path(filename).suffix[1:]
    if file_format not in formats:
        raise RuntimeError(f"Unknown file format: {file_format}")
    return file_format


def open_or_stdio(file, mode: str, *args, **kwargs):
    if file == "-":
        if "r" in mode:
            stream = sys.stdin
        else:
            stream = sys.stdout
        if "b" in mode:
            stream = stream.buffer
        return contextlib.nullcontext(stream)
    else:
        return open(file, mode, *args, **kwargs)


def main(argv: List = None) -> int:
    """Main function for the bertlv module.

    Parse the input file specified on the command line and dump the resulting TLV tree
    to standard output or the optional output file.
    """
    parser = argparse.ArgumentParser(description="BER TLV parser.")
    parser.add_argument("-V", "--version", action="version", version=__version__)
    parser.add_argument(
        "-s",
        "--strict",
        action="store_true",
        help="Enable strict checking of TLV encoding (default: %(default)s)",
    )
    parser.add_argument(
        "-m",
        "--mapping",
        action="append",
        help="Mapping file(s) to use for encoding/decoding (default: %(default)s)",
    )
    parser.add_argument(
        "--input-format",
        choices=INPUT_FORMATS.keys(),
        help="Format to use for the input (default: extension of input file)",
    )
    parser.add_argument(
        "--output-format",
        choices=OUTPUT_FORMATS.keys(),
        help="Format to use for the output (default: extension of input file)",
    )
    parser.add_argument(
        "input", help="Input file to read the TLV tree from",
    )
    parser.add_argument(
        "output",
        nargs="?",
        default="-",
        help="Output file to write the TLV tree to (default: stdout)",
    )

    args = parser.parse_args(argv)

    config.strict_checking = args.strict

    if args.mapping:
        mapper.parse(args.mapping)

    input_format = args.input_format or detect_file_format(args.input, INPUT_FORMATS)
    with open_or_stdio(args.input, "rb") as file:
        tlv_tree = INPUT_FORMATS[input_format](file)

    output_format = args.output_format or detect_file_format(
        args.output, OUTPUT_FORMATS, "txt"
    )
    with open_or_stdio(args.output, "wb") as file:
        OUTPUT_FORMATS[output_format](tlv_tree, file)

    return 0


if __name__ == "__main__":
    # Execute the following lines only when this script is called directly.
    # When it is included from another script they are ignored.
    sys.exit(main())
