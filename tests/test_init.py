import io

from bertlv import tree_from_binary, tree_from_xml, tree_to_binary, tree_to_xml


def test_tree_from_binary_with_bytes(tlv_binary_data, tlv_tree):
    assert tree_from_binary(tlv_binary_data) == tlv_tree

    tree_from_binary(bytearray(tlv_binary_data))
    # noinspection PyTypeChecker
    tree_from_binary(memoryview(tlv_binary_data))


def test_tree_from_binary_with_stream(tlv_binary_data, tlv_tree):
    stream = io.BytesIO(tlv_binary_data)
    assert tree_from_binary(stream) == tlv_tree


def test_tree_from_binary_with_file(tlv_tree, tmp_path):
    test_tree_to_binary_with_file(tlv_tree, tmp_path)
    path = tmp_path / "test.tlv"
    with path.open("rb") as file:
        assert tree_from_binary(file) == tlv_tree


def test_tree_from_xml_with_bytes(tlv_tree, tlv_xml_data):
    assert tree_from_xml(tlv_xml_data) == tlv_tree

    tree_from_xml(bytearray(tlv_xml_data))
    # noinspection PyTypeChecker
    tree_from_xml(memoryview(tlv_xml_data))


def test_tree_from_xml_with_stream(tlv_tree, tlv_xml_data):
    stream = io.BytesIO(tlv_xml_data)
    assert tree_from_xml(stream) == tlv_tree


def test_tree_from_xml_with_file(tlv_tree, tmp_path):
    test_tree_to_xml_with_file(tlv_tree, tmp_path)
    path = tmp_path / "test.xml"
    with path.open("rb") as file:
        assert tree_from_xml(file) == tlv_tree


def test_tree_to_binary_with_bytes(tlv_binary_data, tlv_tree):
    assert tree_to_binary(tlv_tree) == tlv_binary_data


def test_tree_to_binary_with_stream(tlv_binary_data, tlv_tree, tmp_path):
    stream = io.BytesIO()
    tree_to_binary(tlv_tree, stream)
    assert stream.getvalue() == tlv_binary_data


def test_tree_to_binary_with_file(tlv_tree, tmp_path):
    path = tmp_path / "test.tlv"
    with path.open("wb") as file:
        tree_to_binary(tlv_tree, file)


def test_tree_to_xml_with_bytes(tlv_tree, tlv_xml_data):
    assert tree_to_xml(tlv_tree) == tlv_xml_data


def test_tree_to_xml_with_stream(tlv_tree, tlv_xml_data):
    stream = io.BytesIO()
    tree_to_xml(tlv_tree, stream)
    assert stream.getvalue() == tlv_xml_data


def test_tree_to_xml_with_file(tlv_tree, tmp_path):
    path = tmp_path / "test.xml"
    with path.open("wb") as file:
        tree_to_xml(tlv_tree, file)
