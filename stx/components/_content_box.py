from __future__ import annotations

from typing import List, TextIO, Optional

from ._component import Component
from ..compiling.reading.location import Location


class ContentBox(Component):

    def __init__(self, location: Location):
        self.location = location
        self.content: Optional[Component] = None
        self.style = None

    def write_text(self, output: TextIO):
        self.content.write_text(output)

    def get_children(self) -> List[Component]:
        return [self.content]
