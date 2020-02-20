from __future__ import annotations

from typing import List, TextIO

from ._component import Component

# TODO looks like this is not a component per se
from ..compiling.reading.location import Location
from ..data_notation.values import Value
from ..utils.tracked_dict import TrackedDict


class TableRow(Component):

    def __init__(self, location: Location, header: bool):
        self.location = location
        self.header = header
        self.cells: List[Component] = []

    def write_text(self, output: TextIO):
        for cell in self.cells:
            cell.write_text(output)

    def get_children(self) -> List[Component]:
        return self.cells

    def apply_advanced_attributes(self, attributes: TrackedDict[str, Value]):
        pass
