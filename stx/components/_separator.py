from __future__ import annotations

from typing import List, TextIO

from ._component import Component
from ..compiling.reading.location import Location


class Separator(Component):

    def __init__(self, location: Location):
        self.location = location
        self.level = 0

    def write_text(self, output: TextIO):
        pass

    def get_children(self) -> List[Component]:
        return []
