from __future__ import annotations

from typing import List, TextIO

from ._component import Component
from ..compiling.reading.location import Location


class ListBlock(Component):

    def __init__(
            self,
            location: Location,
            ordered: bool):
        self.location = location
        self.ordered = ordered
        self.items: List[Component] = []

    def write_text(self, output: TextIO):
        for item in self.items:
            item.write_text(output)

    def get_children(self) -> List[Component]:
        return self.items
