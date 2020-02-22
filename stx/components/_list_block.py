from __future__ import annotations

from typing import List, TextIO

from ._component import Component, DisplayMode
from ..compiling.reading.location import Location
from ..data_notation.values import Value
from ..utils.tracked_dict import TrackedDict


class ListBlock(Component):

    def __init__(
            self,
            location: Location,
            ordered: bool):
        self.location = location
        self.ordered = ordered
        self.items: List[Component] = []

    @property
    def display_mode(self) -> DisplayMode:
        return DisplayMode.BLOCK

    def write_text(self, output: TextIO):
        for item in self.items:
            item.write_text(output)

    def get_children(self) -> List[Component]:
        return self.items

    def apply_advanced_attributes(self, attributes: TrackedDict[str, Value]):
        pass
