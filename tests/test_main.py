import os

import pytest

import bertlv.__main__

from .test_init import test_tree_to_binary_with_file


def test_runas_module():
    assert os.system("python -m bertlv --help") == 0


def test_entrypoint():
    assert os.system("bertlv --help") == 0


def test_main():
    with pytest.raises(SystemExit, match=r"0$"):
        bertlv.__main__.main(["--help"])


def test_main_with_input_tlv_and_output_txt(capsys, tlv_dump, tlv_tree, tmp_path):
    test_tree_to_binary_with_file(tlv_tree, tmp_path)
    path = tmp_path / "test.tlv"
    exit_code = bertlv.__main__.main([str(path)])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert tlv_dump in captured.out


def test_main_with_input_xml_and_output_txt(capsys, tlv_dump, tlv_tree, tmp_path):
    test_tree_to_binary_with_file(tlv_tree, tmp_path)
    path = tmp_path / "test.tlv"
    exit_code = bertlv.__main__.main([str(path)])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert tlv_dump in captured.out


def test_main_with_unknown_file_format():
    with pytest.raises(RuntimeError, match=r"Unknown file format: jpg$"):
        bertlv.__main__.main(["test.jpg"])


def test_main_with_no_arguments(capsys):
    with pytest.raises(SystemExit, match=r"2$"):
        bertlv.__main__.main([])
    captured = capsys.readouterr()
    assert "error: the following arguments are required: input" in captured.err
