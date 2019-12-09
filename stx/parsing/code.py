import string

from typing import Optional, Tuple, List

from stx.reader import Reader
from stx.utils import Stack
from stx.components.blocks import Block, BComposite, BTitle, BListItem, \
    BElement, BDirective
from stx.components.blocks import BLineText, BSeparator, BTableCell
from stx.components.blocks import BAttribute, BTableRow, BCodeBlock


def parse_code_block(
        reader: Reader, stop_marks: Stack) -> Optional[BCodeBlock]:
    content = parse_text_block(reader, '```')

    if content is None:
        return None

    return BCodeBlock(content)


def parse_ignore_block(
        reader: Reader,
        stop_marks: Stack) -> Optional[Block]:
    content = parse_text_block(reader, '!!!')

    if content is None:
        return None

    return BSeparator()


def parse_text_block(reader: Reader, delimiter: str) -> Optional[str]:
    if not reader.pull(delimiter):
        return None

    indent = reader.column - len(delimiter)

    expect_line_break(reader)

    content = []

    reader.push_indent(indent)

    while not reader.pull(delimiter):
        c = reader.read_char()

        if c is None:
            raise Exception(f'{reader.location}: Expected end of block')

        content.append(c)

    expect_line_break(reader)

    reader.pop_indent()

    return ''.join(content)


def expect_line_break(reader: Reader):
    while reader.pull(' '):
        pass

    if not reader.alive:
        pass
    elif not reader.pull('\n'):
        raise Exception(f'{reader.location}: Expected line break.')

