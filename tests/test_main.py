import os

import pytest

import bertlv.__main__


def test_runas_module():
    assert os.system("python -m bertlv --help") == 0


def test_entrypoint():
    assert os.system("bertlv --help") == 0


def test_main():
    with pytest.raises(SystemExit, match=r"0$"):
        bertlv.__main__.main(["--help"])


def test_main_with_no_arguments(capsys):
    with pytest.raises(SystemExit, match=r"2$"):
        bertlv.__main__.main([])
    captured = capsys.readouterr()
    assert "error: the following arguments are required: input" in captured.err


def test_main_with_input_tlv_and_output_txt(capsys, tlv_file_binary, tlv_dump):
    exit_code = bertlv.__main__.main([str(tlv_file_binary)])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert tlv_dump in captured.out


def test_main_with_input_xml_and_output_txt(capsys, tlv_file_xml, tlv_dump):
    exit_code = bertlv.__main__.main([str(tlv_file_xml)])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert tlv_dump in captured.out


def test_main_with_mapped_input_xml_and_output_txt(
    capsys, tlv_file_mapping, tlv_file_xml_mapped, tlv_dump_mapped
):
    exit_code = bertlv.__main__.main(
        ["--mapping", str(tlv_file_mapping), str(tlv_file_xml_mapped)]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert tlv_dump_mapped in captured.out


def test_main_with_unknown_file_format():
    with pytest.raises(RuntimeError, match=r"Unknown file format: jpg$"):
        bertlv.__main__.main(["test.jpg"])


def test_main_with_standard_input_and_missing_file_format():
    with pytest.raises(RuntimeError, match=r"Unknown file format: $"):
        bertlv.__main__.main(["-"])


def test_main_with_empty_input_file(capsys, tmp_path):
    path = tmp_path / "test.tlv"
    path.touch()
    exit_code = bertlv.__main__.main([str(path), "-"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "root" in captured.out
