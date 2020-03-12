from __future__ import annotations

from typing import List, TextIO

from ._component import Component, DisplayMode
from ..compiling.reading.location import Location
from ..data_notation.values import Value
from ..utils.tracked_dict import TrackedDict


class StyledText(Component):

    def __init__(
            self,
            location: Location,
            contents: List[Component],
            style: str):
        self.location = location
        self.contents = contents
        self.style = style

    @property
    def display_mode(self) -> DisplayMode:
        return DisplayMode.INLINE

    def is_rich(self) -> bool:
        return True

    def write_text(self, output: TextIO):
        for content in self.contents:
            content.write_text(output)

    def get_children(self) -> List[Component]:
        return self.contents

    def apply_advanced_attributes(self, attributes: TrackedDict[str, Value]):
        pass
