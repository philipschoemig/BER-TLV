import sys
from collections import deque
from contextlib import contextmanager
from typing import Any, Iterable
from xml.etree import ElementTree

import pytest

from bertlv import config
from bertlv.parser import (
    TreeBuilder,
    BinaryParser,
    XmlParser,
    TlvInsufficientDataError,
    TlvParsingError,
)
from bertlv.tag import Tag
from bertlv.tree import TlvNode


class TreeBuilderMockUp(TreeBuilder):
    def __init__(self, expected_calls: deque = None):
        super().__init__()
        self.expected_calls = expected_calls

    def close(self) -> TlvNode:
        self.check_empty()
        return super().close()

    def end(self, tag: Tag) -> TlvNode:
        self._check_call("end", [tag.identifier.hex()])
        return super().end(tag)

    def data(self, data: bytes) -> Any:
        self._check_call("data", [data.hex()])
        return super().data(data)

    def start(self, tag: Tag) -> TlvNode:
        self._check_call("start", [tag.identifier.hex()])
        return super().start(tag)

    def check_empty(self):
        assert (
            len(self.expected_calls) == 0
        ), f"expected calls missing: {list(self.expected_calls)}"

    def _check_call(self, name, args):
        if self.expected_calls:
            call = self.expected_calls.popleft()
            assert {name: args} == call


class TestBinaryParser:
    def test_close(self):
        calls = [
            {"start": ["ff60"]},
            {"start": ["5f20"]},
            {"data": ["112233"]},
            {"end": ["5f20"]},
            {"end": ["ff60"]},
        ]
        with self._create_parser(calls) as parser:
            parser.feed(b"\xFF\x60\x06\x5F\x20\x03\x11\x22\x33")
            tree = parser.close()
            assert (
                tree.dump()
                == """Root
└── ff60
    └── 5f20: 112233"""
            )

    def test_close_with_empty_value(self):
        calls = [{"start": ["5f20"]}, {"data": [""]}, {"end": ["5f20"]}]
        with self._create_parser(calls) as parser:
            parser.feed(b"\x5F\x20\x00")
            tree = parser.close()
            assert (
                tree.dump()
                == """Root
└── 5f20: """
            )

        calls = [{"start": ["ff60"]}, {"end": ["ff60"]}]
        with self._create_parser(calls) as parser:
            parser.feed(b"\xFF\x60\x00")
            tree = parser.close()
            assert (
                tree.dump()
                == """Root
└── ff60"""
            )

    def test_close_with_no_data(self):
        with self._create_parser([]) as parser:
            parser.feed(b"")
            tree = parser.close()
            assert tree.dump() == """Root"""

    def test_close_with_incomplete_tag(self):
        with self._create_parser([]) as parser:
            parser.feed(b"\x5F")
            with pytest.raises(
                TlvInsufficientDataError,
                match=r"insufficient data to parse the tag: offset 1$",
            ):
                parser.close()

    def test_close_with_missing_length(self):
        with self._create_parser([]) as parser:
            parser.feed(b"\x5F\x20")
            with pytest.raises(
                TlvInsufficientDataError,
                match=r"insufficient data to parse the length: tag 5f20, offset 2",
            ):
                parser.close()

    def test_close_with_incomplete_length(self):
        with self._create_parser([]) as parser:
            parser.feed(b"\x5F\x20\x81")
            with pytest.raises(
                TlvInsufficientDataError,
                match=r"insufficient data to parse the length: tag 5f20, offset 3",
            ):
                parser.close()

    def test_close_with_missing_value(self):
        with self._create_parser([]) as parser:
            parser.feed(b"\x5F\x20\x03")
            with pytest.raises(
                TlvInsufficientDataError,
                match=r"insufficient data to parse the value: tag 5f20, offset 3",
            ):
                parser.close()

        with self._create_parser([]) as parser:
            parser.feed(b"\xFF\x60\x06")
            with pytest.raises(
                TlvInsufficientDataError,
                match=r"insufficient data to parse the constructed value: tag ff60, offset 3",
            ):
                parser.close()

    def test_close_with_incomplete_value(self):
        with self._create_parser([]) as parser:
            parser.feed(b"\x5F\x20\x03\x11")
            with pytest.raises(
                TlvInsufficientDataError,
                match=r"insufficient data to parse the value: tag 5f20, offset 3",
            ):
                parser.close()

        with self._create_parser([]) as parser:
            parser.feed(b"\xFF\x60\x06\x5F\x20")
            with pytest.raises(
                TlvInsufficientDataError,
                match=r"insufficient data to parse the constructed value: tag ff60, offset 3",
            ):
                parser.close()

    def test_feed_with_invalid_tag(self):
        config.strict_checking = True
        with self._create_parser([]) as parser:
            with pytest.raises(
                TlvParsingError, match=r"error while parsing the tag: offset 3$",
            ):
                parser.feed(b"\x5F\x80\x01")
        config.strict_checking = False

    @contextmanager
    def _create_parser(self, calls: Iterable = None):
        target = None
        if calls is not None:
            expected_calls = deque(calls)
            target = TreeBuilderMockUp(expected_calls)
        parser = BinaryParser(target=target)
        try:
            yield parser
        finally:
            if target and not sys.exc_info()[0]:
                target.check_empty()


class TestXmlParser:
    def test_close(self):
        calls = [
            {"start": ["ff60"]},
            {"start": ["5f20"]},
            {"data": ["112233"]},
            {"end": ["5f20"]},
            {"end": ["ff60"]},
        ]
        with self._create_parser(calls) as parser:
            parser.feed(
                b"""<Tlv>
  <Element Tag="0xFF60">
    <Primitive Tag="0x5F20" Type="Hex">
      112233
    </Primitive>
  </Element>
</Tlv>"""
            )
            tree = parser.close()
            assert (
                tree.dump()
                == """Root
└── ff60
    └── 5f20: 112233"""
            )

    def test_close_with_empty_value(self):
        calls = [
            {"start": ["5f20"]},
            {"data": [""]},
            {"end": ["5f20"]},
        ]
        with self._create_parser(calls) as parser:
            parser.feed(
                b"""<Tlv>
  <Primitive Tag="0x5F20" Type="Hex" />
</Tlv>"""
            )
            tree = parser.close()
            assert (
                tree.dump()
                == """Root
└── 5f20: """
            )

        calls = [{"start": ["ff60"]}, {"end": ["ff60"]}]
        with self._create_parser(calls) as parser:
            parser.feed(
                b"""<Tlv>
  <Element Tag="0xFF60" />
</Tlv>"""
            )
            tree = parser.close()
            assert (
                tree.dump()
                == """Root
└── ff60"""
            )

    def test_close_with_type_ascii(self):
        with self._create_parser([]) as parser:
            parser.feed(b"""<Primitive Tag="0x5F20" Type="ASCII">123</Primitive>""")
            tree = parser.close()
            assert (
                tree.dump()
                == """Root
└── 5f20: 313233"""
            )

    def test_close_with_type_hex(self):
        with self._create_parser([]) as parser:
            parser.feed(b"""<Primitive Tag="0x5F20" Type="Hex">123</Primitive>""")
            tree = parser.close()
            assert (
                tree.dump()
                == """Root
└── 5f20: 0123"""
            )

    def test_close_with_no_data(self):
        with self._create_parser([]) as parser:
            parser.feed(b"")
            with pytest.raises(
                ElementTree.ParseError, match="no element found: line 1, column 0"
            ):
                parser.close()

    def test_close_with_forced_constructed(self):
        calls = [
            {"start": ["df51"]},
            {"start": ["5f20"]},
            {"data": ["112233"]},
            {"end": ["5f20"]},
            {"end": ["df51"]},
        ]
        with self._create_parser(calls) as parser:
            parser.feed(
                b"""<Tlv>
  <Element Tag="0xDF51" Force="True">
    <Primitive Tag="0x5F20" Type="Hex">
      112233
    </Primitive>
  </Element>
</Tlv>"""
            )
            tree = parser.close()
            assert (
                tree.dump()
                == """Root
└── df51
    └── 5f20: 112233"""
            )

    def test_feed_with_partial_data(self):
        calls = [{"start": ["5f20"]}]
        with self._create_parser(calls) as parser:
            parser.feed(
                b"""<Tlv>
<Primitive Tag="0x5F20" Type="Hex">"""
            )

        calls = [{"start": ["ff60"]}]
        with self._create_parser(calls) as parser:
            parser.feed(
                b"""<Tlv>
<Element Tag="0xFF60">"""
            )

    def test_feed_with_missing_tag(self):
        with self._create_parser([]) as parser:
            with pytest.raises(
                TlvParsingError,
                match=r"error while parsing the tag: element '<Element />'$",
            ) as exc_info:
                parser.feed(b"<Element />")
            assert type(exc_info.value.__cause__) == ValueError
            assert str(exc_info.value.__cause__) == "missing 'Tag' attribute"

    def test_feed_with_invalid_tag(self):
        with self._create_parser([]) as parser:
            with pytest.raises(
                TlvParsingError,
                match=r"error while parsing the tag: element '<Primitive Tag=\"Invalid\" />'$",
            ) as exc_info:
                parser.feed(b"""<Primitive Tag="Invalid" />""")
            assert type(exc_info.value.__cause__) == ValueError
            assert (
                str(exc_info.value.__cause__)
                == "non-hexadecimal number found in fromhex() arg at position 0"
            )

        with self._create_parser([]) as parser:
            with pytest.raises(
                TlvParsingError,
                match=r"error while parsing the tag: element '<Primitive Tag=\"0x5F\" />'$",
            ) as exc_info:
                parser.feed(b"""<Primitive Tag="0x5F" />""")
            assert type(exc_info.value.__cause__) == ValueError
            assert (
                str(exc_info.value.__cause__) == "tag is missing subsequent octets: 5f"
            )

    def test_feed_with_incorrect_xml_tag(self):
        with self._create_parser([]) as parser:
            with pytest.raises(
                TlvParsingError,
                match=r"error while parsing the tag: element '<Primitive Tag=\"0xFF60\" />'$",
            ) as exc_info:
                parser.feed(b"""<Primitive Tag="0xFF60" />""")
            assert type(exc_info.value.__cause__) == AssertionError

        with self._create_parser([]) as parser:
            with pytest.raises(
                TlvParsingError,
                match=r"error while parsing the tag: element '<Element Tag=\"0x5F20\" />'$",
            ) as exc_info:
                parser.feed(b"""<Element Tag="0x5F20" />""")
            assert type(exc_info.value.__cause__) == AssertionError

    def test_feed_with_invalid_type_attribute(self):
        with self._create_parser([]) as parser:
            with pytest.raises(
                TlvParsingError,
                match=r"error while parsing the value: tag 5f20, element "
                r"'<Primitive Tag=\"0x5F20\" Type=\"ANSI\">112233</Primitive>'$",
            ) as exc_info:
                parser.feed(
                    b"""<Primitive Tag="0x5F20" Type="ANSI">112233</Primitive>"""
                )
            assert type(exc_info.value.__cause__) == ValueError
            assert (
                str(exc_info.value.__cause__) == "invalid 'Type' attribute value: ANSI"
            )

    @contextmanager
    def _create_parser(self, calls: Iterable = None):
        target = None
        if calls is not None:
            expected_calls = deque(calls)
            target = TreeBuilderMockUp(expected_calls)
        parser = XmlParser(target=target)
        try:
            yield parser
        finally:
            if target and not sys.exc_info()[0]:
                target.check_empty()
