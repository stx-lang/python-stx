from __future__ import annotations

from typing import List, TextIO

from ._component import Component
from ..compiling.reading.location import Location


class RawText(Component):  # TODO rename to embedded block

    def __init__(self, location: Location, text: str):
        # TODO add origin
        self.location = location
        self.content = text

    def write_text(self, output: TextIO):
        output.write(self.content)

    def get_children(self) -> List[Component]:
        return []
