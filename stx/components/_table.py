from __future__ import annotations

from typing import List, Optional, TextIO

from ._component import Component
from ._table_row import TableRow
from ..compiling.reading.location import Location


class Table(Component):

    def __init__(self, location: Location):
        self.location = location
        self.rows: List[TableRow] = []
        self.caption: Optional[Component] = None
        self.number: Optional[str] = None

    def write_text(self, output: TextIO):
        for row in self.rows:
            row.write_text(output)

    def get_children(self) -> List[Component]:
        if self.caption is not None:
            return [self.caption, *self.rows]

        return self.rows

    def get_last_row(self) -> Optional[TableRow]:
        if len(self.rows) > 0:
            return self.rows[-1]
        return None
