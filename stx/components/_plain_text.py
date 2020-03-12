from __future__ import annotations

from typing import List, TextIO

from ._component import Component, DisplayMode
from ..compiling.reading.location import Location
from ..data_notation.values import Value
from ..utils.tracked_dict import TrackedDict


class PlainText(Component):

    def __init__(self, location: Location, text: str):
        self.location = location
        self.content = text

    @property
    def display_mode(self) -> DisplayMode:
        return DisplayMode.INLINE

    def is_rich(self) -> bool:
        return False

    def write_text(self, output: TextIO):
        output.write(self.content)

    def get_children(self) -> List[Component]:
        return []

    def apply_advanced_attributes(self, attributes: TrackedDict[str, Value]):
        pass
