import io

from bertlv import (
    tree_from_binary,
    tree_from_xml,
    tree_to_binary,
    tree_to_text,
    tree_to_xml,
)


def test_tree_from_binary_with_bytes(tlv_data_binary, tlv_tree):
    assert tree_from_binary(tlv_data_binary) == tlv_tree

    tree_from_binary(bytearray(tlv_data_binary))
    # noinspection PyTypeChecker
    tree_from_binary(memoryview(tlv_data_binary))


def test_tree_from_binary_with_stream(tlv_data_binary, tlv_tree):
    stream = io.BytesIO(tlv_data_binary)
    assert tree_from_binary(stream) == tlv_tree


def test_tree_from_binary_with_file(tlv_file_binary, tlv_tree):
    with tlv_file_binary.open("rb") as file:
        assert tree_from_binary(file) == tlv_tree


def test_tree_from_xml_with_bytes(tlv_data_xml, tlv_tree):
    assert tree_from_xml(tlv_data_xml) == tlv_tree

    tree_from_xml(bytearray(tlv_data_xml))
    # noinspection PyTypeChecker
    tree_from_xml(memoryview(tlv_data_xml))


def test_tree_from_xml_with_stream(tlv_data_xml, tlv_tree):
    stream = io.BytesIO(tlv_data_xml)
    assert tree_from_xml(stream) == tlv_tree


def test_tree_from_xml_with_file(tlv_file_xml, tlv_tree):
    with tlv_file_xml.open("rb") as file:
        assert tree_from_xml(file) == tlv_tree


def test_tree_to_binary_with_bytes(tlv_data_binary, tlv_tree):
    assert tree_to_binary(tlv_tree) == tlv_data_binary


def test_tree_to_binary_with_stream(tlv_data_binary, tlv_tree):
    stream = io.BytesIO()
    tree_to_binary(tlv_tree, stream)
    assert stream.getvalue() == tlv_data_binary


def test_tree_to_binary_with_file(tlv_file_binary, tlv_tree, tmp_path):
    path = tmp_path / "test.tlv"
    with path.open("wb") as file:
        tree_to_binary(tlv_tree, file)
    assert path.read_bytes() == tlv_file_binary.read_bytes()


def test_tree_to_text_with_bytes(tlv_data_text, tlv_tree):
    assert tree_to_text(tlv_tree) == tlv_data_text


def test_tree_to_text_with_stream(tlv_data_text, tlv_tree):
    stream = io.BytesIO()
    tree_to_text(tlv_tree, stream)
    assert stream.getvalue() == tlv_data_text


def test_tree_to_text_with_file(tlv_file_text, tlv_tree, tmp_path):
    path = tmp_path / "test.txt"
    with path.open("wb") as file:
        tree_to_text(tlv_tree, file)
    assert path.read_bytes() == tlv_file_text.read_bytes()


def test_tree_to_xml_with_bytes(tlv_data_xml, tlv_tree):
    assert tree_to_xml(tlv_tree) == tlv_data_xml


def test_tree_to_xml_with_stream(tlv_data_xml, tlv_tree):
    stream = io.BytesIO()
    tree_to_xml(tlv_tree, stream)
    assert stream.getvalue() == tlv_data_xml


def test_tree_to_xml_with_file(tlv_file_xml, tlv_tree, tmp_path):
    path = tmp_path / "test.xml"
    with path.open("wb") as file:
        tree_to_xml(tlv_tree, file)
    assert path.read_bytes() == tlv_file_xml.read_bytes()
