from __future__ import annotations

import re
from io import StringIO
from typing import List, Iterable, Optional, TextIO

from ._component import Component
from ..compiling.reading.location import Location
from ..data_notation.values import Value
from ..utils.tracked_dict import TrackedDict


class ElementReference:

    def __init__(self, title: str, reference: str, number: Optional[str]):
        self.title = title
        self.reference = reference
        self.number = number
        self.elements: List[ElementReference] = []


class TableOfContents(Component):

    def __init__(self, location: Location):
        self.location = location
        self.title: Optional[str] = None
        self.elements: List[ElementReference] = []

    def write_text(self, output: TextIO):
        pass

    def get_children(self) -> List[Component]:
        return []

    def apply_advanced_attributes(self, attributes: TrackedDict[str, Value]):
        title_value = attributes.get('title')

        if title_value is not None:
            self.title = title_value.to_str()

