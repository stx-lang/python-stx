from __future__ import annotations

from typing import List, TextIO, Optional

from ._component import Component, DisplayMode
from ..compiling.reading.location import Location
from ..data_notation.values import Value
from ..utils.tracked_dict import TrackedDict


class Literal(Component):

    def __init__(
            self,
            location: Location,
            text: str,
            lang: Optional[str] = None,  # TODO remove this field
            source: Optional[str] = None):
        self.location = location
        self.text = text
        self.lang = lang
        self.source = source

    @property
    def display_mode(self) -> DisplayMode:
        return DisplayMode.DEFAULT

    def is_rich(self) -> bool:
        return False

    def write_text(self, output: TextIO):
        output.write(self.text)

    def get_children(self) -> List[Component]:
        return []

    def apply_advanced_attributes(self, attributes: TrackedDict[str, Value]):
        pass
