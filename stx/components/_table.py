from __future__ import annotations

import re
from io import StringIO
from typing import List, Iterable, Optional, TextIO

from stx.design.attributes_map import AttributesMap

from stx.utils.strs import crop_text
from ._table_row import TableRow

from ._component import Component
from ..utils.stx_error import StxError


class Table(Component):

    def __init__(self, rows: List[TableRow]):
        self.rows = rows
        self.caption = None
        self.number = None

    def __repr__(self):
        return f'Table<{len(self.rows)} row(s)>'

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
