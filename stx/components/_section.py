from __future__ import annotations

from typing import List, TextIO, Optional

from ._component import Component, DisplayMode
from ..compiling.reading.location import Location
from ..data_notation.values import Value
from ..utils.tracked_dict import TrackedDict


class Section(Component):

    def __init__(
            self,
            location: Location,
            level: int):
        self.location = location
        self.level = level
        self.heading: Optional[Component] = None
        self.content: Optional[Component] = None
        self.type: Optional[str] = None
        self.number: Optional[str] = None

    @property
    def display_mode(self) -> DisplayMode:
        return DisplayMode.BLOCK

    def is_rich(self) -> bool:
        return True

    def write_text(self, output: TextIO):
        self.heading.write_text(output)
        self.content.write_text(output)

    def get_children(self) -> List[Component]:
        return [self.heading, self.content]

    def apply_advanced_attributes(self, attributes: TrackedDict[str, Value]):
        pass
