from __future__ import annotations

from typing import List, TextIO

from ._component import Component
from ..compiling.reading.location import Location


class Figure(Component):

    def __init__(
            self,
            location: Location,
            content: Component,
            caption: Component):
        # TODO add flag for caption first or last
        self.location = location
        self.content = content
        self.caption = caption
        self.number = None

    def write_text(self, output: TextIO):
        self.caption.write_text(output)
        self.content.write_text(output)

    def get_children(self) -> List[Component]:
        return [self.caption, self.content]
