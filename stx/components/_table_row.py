from __future__ import annotations

import re
from io import StringIO
from typing import List, Iterable, Optional, TextIO

from stx.design.attributes_map import AttributesMap

from stx.utils.strs import crop_text

from ._component import Component
from ..utils.stx_error import StxError


class TableRow(Component):

    def __init__(self, cells: List[Component], header: bool):
        self.cells = cells
        self.header = header

    def __repr__(self):
        return f'TableRow<{len(self.cells)} cell(s)>'

    def write_text(self, output: TextIO):
        for cell in self.cells:
            cell.write_text(output)

    def get_children(self) -> List[Component]:
        return self.cells

    def pop_attributes(self, attributes: dict):
        raise StxError('not implemented')
