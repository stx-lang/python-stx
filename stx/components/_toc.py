from __future__ import annotations

import re
from io import StringIO
from typing import List, Iterable, Optional, TextIO

from ._component import Component
from ..compiling.reading.location import Location


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
