from __future__ import annotations

from typing import List, TextIO

from ._component import Component
from ..compiling.reading.location import Location


class PlainText(Component):

    def __init__(self, location: Location, text: str):
        self.location = location
        self.content = text

    def write_text(self, output: TextIO):
        output.write(self.content)

    def get_children(self) -> List[Component]:
        return []
