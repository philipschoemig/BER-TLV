from abc import ABC, abstractmethod
from typing import Any


class Mapping:
    pass


class MapperBase(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def process(self, item: Any) -> Any:
        """Process the mapping for the given item and return the result."""


class XmlTlvMapper:
    pass
