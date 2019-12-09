from typing import Optional

import stx.parsing.block as block

from stx.components.blocks import BTitle, BListItem, BElement
from stx.reader import Reader
from stx.utils import Stack


def parse_title(reader: Reader, stop_marks: Stack) -> Optional[BTitle]:
    if not reader.pull('='):
        return None

    level = 1

    while reader.pull('='):
        level += 1

    while reader.pull(' '):
        pass

    reader.push_indent(reader.column)

    content = block.parse_block(reader, stop_marks)

    reader.pop_indent()

    return BTitle(content, level)


def parse_list(reader: Reader, stop_marks: Stack) -> Optional[BListItem]:
    # TODO refactor to Element

    if reader.pull('-'):
        ordered = False
    elif reader.pull('.'):
        ordered = True
    else:
        return None

    while reader.pull(' '):
        pass

    reader.push_indent(reader.column)

    content = block.parse_block(reader, stop_marks)

    reader.pop_indent()

    return BListItem(content, ordered)


def parse_element(reader: Reader, stop_marks: Stack) -> Optional[BElement]:
    if not reader.any('>', '<'):
        return None

    mark = reader.read_char()

    while reader.pull(' '):
        pass

    reader.push_indent(reader.column)

    content = block.parse_block(reader, stop_marks)

    reader.pop_indent()

    return BElement(content, mark)