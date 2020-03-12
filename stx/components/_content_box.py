from __future__ import annotations

from typing import List, TextIO, Optional

from ._component import Component, DisplayMode
from ..compiling.reading.location import Location
from ..data_notation.values import Value
from ..utils.tracked_dict import TrackedDict


class ContentBox(Component):  # TODO rename to box

    def __init__(self, location: Location):
        self.location = location
        self.content: Optional[Component] = None
        self.style = None

    @property
    def display_mode(self) -> DisplayMode:
        return DisplayMode.BLOCK

    def is_rich(self) -> bool:
        return True

    def write_text(self, output: TextIO):
        self.content.write_text(output)

    def get_children(self) -> List[Component]:
        return [self.content]

    def apply_advanced_attributes(self, attributes: TrackedDict[str, Value]):
        style_value = attributes.get('style')

        if style_value is not None:
            self.style = style_value.to_str()
