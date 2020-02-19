from __future__ import annotations

from typing import List, TextIO

from ._component import Component
from ..compiling.reading.location import Location


class Image(Component):

    def __init__(
            self,
            location: Location,
            src: str,
            alt: str):
        self.location = location
        self.src = src
        self.alt = alt

    def write_text(self, output: TextIO):
        if self.alt:
            output.write(self.alt)

    def get_children(self) -> List[Component]:
        return []
