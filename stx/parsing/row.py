from typing import Optional

import stx.parsing.block as block

from stx.components.blocks import BLineText, BSeparator, BTableCell
from stx.components.blocks import BTableRow
from stx.reader import Reader
from stx.utils import Stack


def parse(
        reader: Reader, stop_marks: Stack) -> Optional[BTableRow]:
    cells = []

    while True:
        cell = parse_table_cell(reader, stop_marks)

        if cell is None:
            break

        if isinstance(cell.content, BSeparator):
            break

        cells.append(cell)

    if len(cells) == 0:
        return None

    return BTableRow(cells)


def parse_table_cell(
        reader: Reader, stop_marks: Stack) -> Optional[BTableCell]:
    if not reader.pull('|'):
        return None

    while reader.pull(' '):
        pass

    if reader.test('|'):
        return BTableCell(BLineText(''))

    stop_marks.push('|')
    reader.push_indent(reader.column)

    content = block.parse(reader, stop_marks)

    reader.pop_indent()
    stop_marks.pop()

    return BTableCell(content)

