from __future__ import annotations

from typing import List, TextIO

from ._component import Component, DisplayMode
from ..compiling.reading.location import Location
from ..data_notation.values import Value
from ..utils.tracked_dict import TrackedDict


# TODO this component may be replaced by Composite

class Paragraph(Component):

    def __init__(self, location: Location, contents: List[Component]):
        self.location = location
        self.contents = contents

    @property
    def display_mode(self) -> DisplayMode:
        return DisplayMode.BLOCK

    def is_rich(self) -> bool:
        for c in self.contents:
            if c.is_rich():
                return True
        return False

    def write_text(self, output: TextIO):
        for component in self.contents:
            component.write_text(output)

    def get_children(self) -> List[Component]:
        return self.contents

    def apply_advanced_attributes(self, attributes: TrackedDict[str, Value]):
        pass
