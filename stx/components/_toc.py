from __future__ import annotations

import re
from io import StringIO
from typing import List, Iterable, Optional, TextIO

from ._component import Component, DisplayMode
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

    def __init__(self, location: Location, title: Optional[str]):
        self.location = location
        self.title = title
        self.elements: List[ElementReference] = []

    @property
    def display_mode(self) -> DisplayMode:
        return DisplayMode.BLOCK

    def is_rich(self) -> bool:
        return True

    def write_text(self, output: TextIO):
        pass

    def get_children(self) -> List[Component]:
        return []

    def apply_advanced_attributes(self, attributes: TrackedDict[str, Value]):
        pass
