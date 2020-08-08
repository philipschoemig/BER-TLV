import io

from bertlv import tree_from_binary, tree_from_xml, tree_to_binary, tree_to_xml

from .test_tree import _test_binary_data, _test_tree, _test_xml_data


def test_tree_from_binary_with_bytes():
    data = _test_binary_data()
    assert tree_from_binary(data) == _test_tree()

    tree_from_binary(bytearray(data))
    # noinspection PyTypeChecker
    tree_from_binary(memoryview(data))


def test_tree_from_binary_with_stream():
    stream = io.BytesIO(_test_binary_data())
    assert tree_from_binary(stream) == _test_tree()


def test_tree_from_binary_with_file(tmp_path):
    test_tree_to_binary_with_file(tmp_path)
    path = tmp_path / "test.tlv"
    with path.open("rb") as file:
        assert tree_from_binary(file) == _test_tree()


def test_tree_from_xml_with_bytes():
    data = _test_xml_data()
    assert tree_from_xml(data) == _test_tree()

    tree_from_xml(bytearray(data))
    # noinspection PyTypeChecker
    tree_from_xml(memoryview(data))


def test_tree_from_xml_with_stream():
    stream = io.BytesIO(_test_xml_data())
    assert tree_from_xml(stream) == _test_tree()


def test_tree_from_xml_with_file(tmp_path):
    test_tree_to_xml_with_file(tmp_path)
    path = tmp_path / "test.xml"
    with path.open("rb") as file:
        assert tree_from_xml(file) == _test_tree()


def test_tree_to_binary_with_bytes():
    data = tree_to_binary(_test_tree())
    assert data == _test_binary_data()


def test_tree_to_binary_with_stream(tmp_path):
    stream = io.BytesIO()
    tree_to_binary(_test_tree(), stream)
    assert stream.getvalue() == _test_binary_data()


def test_tree_to_binary_with_file(tmp_path):
    path = tmp_path / "test.tlv"
    with path.open("wb") as file:
        tree_to_binary(_test_tree(), file)


def test_tree_to_xml_with_bytes():
    data = tree_to_xml(_test_tree())
    assert data == _test_xml_data()


def test_tree_to_xml_with_stream():
    stream = io.BytesIO()
    tree_to_xml(_test_tree(), stream)
    assert stream.getvalue() == _test_xml_data()


def test_tree_to_xml_with_file(tmp_path):
    path = tmp_path / "test.xml"
    with path.open("wb") as file:
        tree_to_xml(_test_tree(), file)
