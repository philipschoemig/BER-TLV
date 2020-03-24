from collections.abc import Iterator


class Stream(Iterator):
    def __init__(self, data: bytes):
        self._data = data
        self._index = 0
        self._index_queue = []

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._data):
            raise StopIteration
        item = self._data[self._index]
        self._index += 1
        return item

    def __enter__(self):
        self._index_queue.append(self._index)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._index = self._index_queue.pop()

    def is_empty(self) -> bool:
        return self._index >= len(self._data)

    def peek(self) -> int:
        return self._data[self._index]

    @property
    def index(self) -> int:
        return self._index

    @property
    def remaining(self) -> bytes:
        return self._data[self._index :]  # noqa: E203
