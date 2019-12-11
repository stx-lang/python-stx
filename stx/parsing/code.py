from typing import Optional

from stx.components.blocks import BCodeBlock
from stx.components.blocks import BSeparator
from stx.components.blocks import Block
from stx.reader import Reader
from stx.utils import Stack

# TODO make code block class more generic


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

    if len(content) > 0 and content[-1] == '\n':
        content.pop()

    return ''.join(content)


def expect_line_break(reader: Reader):
    while reader.pull(' '):
        pass

    if not reader.alive:
        pass
    elif not reader.pull('\n'):
        raise Exception(f'{reader.location}: Expected line break.')

