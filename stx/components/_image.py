from __future__ import annotations

from typing import List, TextIO

from ._component import Component, DisplayMode
from ..compiling.reading.location import Location
from ..data_notation.values import Value
from ..utils.tracked_dict import TrackedDict


class Image(Component):

    def __init__(
            self,
            location: Location,
            src: str,
            alt: str):
        self.location = location
        self.src = src
        self.alt = alt

    @property
    def display_mode(self) -> DisplayMode:
        return DisplayMode.DEFAULT

    def is_rich(self) -> bool:
        return True

    def write_text(self, output: TextIO):
        if self.alt:
            output.write(self.alt)

    def get_children(self) -> List[Component]:
        return []

    def apply_advanced_attributes(self, attributes: TrackedDict[str, Value]):
        pass
