from __future__ import annotations

from typing import List, TextIO

from ._component import Component, DisplayMode
from ..compiling.reading.location import Location
from ..data_notation.values import Value
from ..utils.tracked_dict import TrackedDict


class Separator(Component):

    def __init__(self, location: Location):
        self.location = location
        self.level = 0

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
