from __future__ import annotations

from typing import List, Optional, TextIO

from ._component import Component
from ..compiling.reading.location import Location
from ..data_notation.values import Entry


class MacroText(Component):

    def __init__(
            self,
            location: Location,
            entry: Entry):
        self.location = location
        self.entry = entry
        self.content: Optional[Component] = None

    def write_text(self, output: TextIO):
        if self.content is not None:
            self.content.write_text(output)

    def get_children(self) -> List[Component]:
        if self.content is None:
            return []
        return [self.content]
