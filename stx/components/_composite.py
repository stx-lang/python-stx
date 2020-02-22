from __future__ import annotations

from typing import List, Optional, TextIO

from ._component import Component, DisplayMode
from ..compiling.reading.location import Location
from ..data_notation.values import Value
from ..utils.tracked_dict import TrackedDict


class Composite(Component):

    def __init__(
            self,
            location: Location,
            components: Optional[List[Component]] = None):
        self.location = location
        self.components = components if components is not None else []

    @property
    def display_mode(self) -> DisplayMode:
        return DisplayMode.compute_display_mode(self.components)

    def write_text(self, output: TextIO):
        for component in self.components:
            component.write_text(output)

    def get_children(self) -> List[Component]:
        return self.components

    def apply_advanced_attributes(self, attributes: TrackedDict[str, Value]):
        pass
