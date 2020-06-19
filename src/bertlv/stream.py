import io
import sys
from collections.abc import Iterator
from contextlib import contextmanager


class BufferedStream(Iterator):
    def __init__(self):
        self.input = io.BytesIO()
        self.pos_queue = []

    @contextmanager
    def rollback(self):
        self.pos_queue.append(self.input.tell())
        try:
            yield
        finally:
            pos = self.pos_queue.pop()
            if sys.exc_info()[0]:
                self.input.seek(pos)

    def __iter__(self):
        return self

    def __next__(self):
        data = self.input.read(1)
        if not data:
            raise StopIteration
        return data[0]

    def is_eof(self) -> bool:
        return self.input.tell() >= len(self.input.getvalue())

    def size(self) -> int:
        pos = self.input.tell()
        try:
            end_pos = self.input.seek(0, io.SEEK_END)
        finally:
            self.input.seek(pos)
        return end_pos - pos

    def close(self) -> None:
        self.input.close()
        self.pos_queue = []

    def read(self, size: int = -1) -> bytes:
        return self.input.read(size)

    def write(self, data: bytes) -> int:
        return self.input.write(data)

    def push(self, data: bytes) -> None:
        pos = self.input.tell()
        try:
            self.input.seek(0, io.SEEK_END)
            self.input.write(data)
        finally:
            self.input.seek(pos)

    def tell(self) -> int:
        return self.input.tell()
