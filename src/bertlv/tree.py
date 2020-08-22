from abc import ABC, abstractmethod
from functools import total_ordering
from typing import Any, Callable, Iterable, Optional

from anytree import Node, RenderTree, Resolver, ResolverError

from .tag import RootTag, Tag


class TlvError(Exception):
    def __init__(
        self, message: str, **kwargs,
    ):
        args = ""
        if kwargs:
            args = ": "
            args += ", ".join([f"{key} {value}" for key, value in kwargs.items()])
        super().__init__(f"{message}{args}")


@total_ordering
class TlvNode(Node):
    _value = None

    def __init__(
        self,
        tag: Tag,
        value: Optional[bytes] = None,
        parent: "TlvNode" = None,
        children: Iterable["TlvNode"] = None,
    ):
        super().__init__(repr(tag))
        self.tag = tag
        if value:
            self.value = value
        self.parent = parent
        if children:
            self.children = children

    def __eq__(self, other: "TlvNode"):
        return self.tag == other.tag

    def __lt__(self, other: "TlvNode"):
        return self.tag < other.tag

    def __str__(self):
        return self.separator.join([""] + [str(node.name) for node in self.path])

    def _pre_attach(self, parent):
        if not parent.is_constructed():
            raise TlvError("Can not attach to primitive node", tag=repr(parent.tag))

    @property
    def value(self) -> bytes:
        if self._value:
            return self._value
        return bytes()

    @value.setter
    def value(self, value: bytes):
        if self.is_constructed():
            raise TlvError("Can not set value on constructed node", tag=repr(self.tag))
        self._value = value

    @property
    def length(self) -> int:
        if self._value:
            return len(self._value)
        return 0

    def is_constructed(self) -> bool:
        return self.tag.is_constructed()

    def dump(self) -> str:
        """Return a string representing the tree starting at this node."""
        text = ""
        for pre, _, node in RenderTree(self):
            if text:
                text += "\n"
            text += f"{pre}{repr(node.tag)}"
            if not node.is_constructed():
                text += f": {node.value.hex()}"
        return text

    def resolve(self, path: str) -> "TlvNode":
        """Return the node at *path*."""
        path = path.lower()
        try:
            node = Resolver().get(self, path)
        except ResolverError as error:
            raise TlvError(
                f"Can not resolve path '{path}' from this node", tag=repr(self.tag)
            ) from error
        return node


class Tree(TlvNode):
    def __init__(self, children: Iterable[TlvNode] = None):
        super().__init__(RootTag(), children=children)


class BuilderBase(ABC):
    @abstractmethod
    def close(self) -> Tree:
        """Flush the builder buffers, and return the tree."""

    @abstractmethod
    def end(self, tag: Tag) -> Any:
        """Close the current TLV node."""

    @abstractmethod
    def data(self, data: bytes) -> Any:
        """Add a value to the current TLV node."""

    @abstractmethod
    def start(self, tag: Tag) -> Any:
        """Open a new TLV node with the given tag."""


class TreeBuilder(BuilderBase):
    def __init__(self, node_factory: Callable = None):
        self._factory = node_factory or TlvNode

        self._tree = Tree()
        self._current = self._tree

    def close(self) -> Tree:
        """Flush the builder buffers, and return the tree."""
        if self._current is not self._tree:
            raise TlvError(f"Missing end tag for '{self._current}'")
        return self._tree

    def end(self, tag: Tag) -> TlvNode:
        """Close the current TLV node. Return the closed node."""
        if self._current.tag != tag:
            raise TlvError(f"End tag mismatch for '{self._current}', got {repr(tag)}")
        node = self._current
        self._current = self._current.parent
        return node

    def data(self, data: bytes) -> Any:
        """Add a value to the current TLV node."""
        self._current.value = data

    def start(self, tag: Tag) -> TlvNode:
        """Open a new TLV node with the given tag. Return the opened node."""
        node = self._factory(tag, parent=self._current)
        self._current = node
        return node
