from __future__ import annotations

from typing import List, Optional, TextIO

from ._component import Component, DisplayMode
from ..compiling.reading.location import Location
from ..data_notation.values import Value
from ..utils.stx_error import StxError
from ..utils.tracked_dict import TrackedDict


DIR_ROW = 'row'
DIR_COLUMN = 'col'


class Layout(Component):

    def __init__(
            self,
            location: Location,
            components: List[Component],
            direction: str):
        self.location = location
        self.components = components

        if direction not in [DIR_ROW, DIR_COLUMN]:
            raise StxError(f'Not allowed direction: {direction}', location)

        self.direction = direction

    @property
    def display_mode(self) -> DisplayMode:
        return DisplayMode.compute_display_mode(self.components)

    def is_rich(self) -> bool:
        for c in self.components:
            if c.is_rich():
                return True
        return False

    def write_text(self, output: TextIO):
        for component in self.components:
            component.write_text(output)

    def get_children(self) -> List[Component]:
        return self.components

    def apply_advanced_attributes(self, attributes: TrackedDict[str, Value]):
        pass
