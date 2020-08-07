import pytest

from bertlv.stream import BufferedStream


class TestBufferedStream:
    def test_init(self):
        stream = BufferedStream()
        assert stream.size() == 0

    def test_iter(self):
        stream = BufferedStream()
        array = bytearray()
        for b in stream:
            array += b
        assert array == b""

    def test_next(self):
        stream = BufferedStream()
        with pytest.raises(StopIteration):
            next(stream)
        stream.push(b"\x10\x21\x42\x84")
        assert next(stream) == 0x10
        assert next(stream) == 0x21

    def test_rollback(self):
        stream = BufferedStream()
        stream.push(b"\x10\x21\x42\x84")
        with pytest.raises(StopIteration):
            with stream.rollback(StopIteration):
                stream.read()
                assert stream.tell() == 4
                next(stream)
        assert stream.tell() == 0

    def test_is_eof(self, benchmark):
        stream = BufferedStream()
        assert stream.is_eof()
        stream.push(b"\x10\x21\x42\x84")
        assert not benchmark(stream.is_eof)
        stream.read()
        assert stream.is_eof()

    def test_size(self, benchmark):
        stream = BufferedStream()
        assert stream.size() == 0
        stream.push(b"\x10\x21\x42\x84")
        assert benchmark(stream.size) == 4
        stream.read(2)
        assert stream.size() == 2

    def test_close(self):
        stream = BufferedStream()
        stream.close()
        with pytest.raises(ValueError, match=r"I/O operation on closed file.$"):
            stream.tell()

    def test_read(self):
        stream = BufferedStream()
        assert stream.read() == b""

        stream.push(b"\x10\x21\x42\x84")
        assert stream.read(1) == b"\x10"
        assert stream.read() == b"\x21\x42\x84"
        assert stream.read() == b""

    def test_write(self):
        stream = BufferedStream()
        assert stream.write(b"\x10\x21\x42\x84") == 4

    def test_push(self):
        stream = BufferedStream()
        assert stream.push(b"\x10\x21\x42\x84") is None
        assert stream.tell() == 0

    def test_tell(self):
        stream = BufferedStream()
        assert stream.tell() == 0
        stream.push(b"\x10\x21\x42\x84")
        assert stream.tell() == 0
        stream.read(2)
        assert stream.tell() == 2
        stream.write(b"\x24")
        assert stream.tell() == 3
        stream.read(2)
        assert stream.tell() == 4
        stream.write(b"\x68")
        assert stream.tell() == 5
