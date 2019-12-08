import string

from typing import Optional

from stx.reader import Reader
from stx.utils import Stack
from stx.components.blocks import Block, BComposite, BTitle, BListItem, \
    BElement
from stx.components.blocks import BLineText, BSeparator, BTableCell
from stx.components.blocks import BAttribute, BTableRow, BCodeBlock


def parse_block(reader: Reader, stop_marks: Stack) -> Block:
    components = []

    while True:
        if reader.test(stop_marks.peek()):
            break

        component = (parse_separator(reader, stop_marks) or
                     parse_title(reader, stop_marks) or
                     parse_list(reader, stop_marks) or
                     parse_element(reader, stop_marks) or
                     parse_table_row(reader, stop_marks) or
                     parse_code_block(reader, stop_marks) or
                     parse_ignore_block(reader, stop_marks) or
                     parse_attribute(reader, stop_marks) or
                     parse_line_text(reader, stop_marks))

        if component is None:
            break
        elif (len(components) > 0
              and isinstance(components[-1], BSeparator)
              and isinstance(component, BSeparator)):
            # Collapse multiple separators into one
            components[-1].size += 1
        else:
            components.append(component)

    if len(components) == 0:
        return BSeparator()
    if len(components) == 1:
        return components[0]

    return BComposite(components)


def parse_separator(
        reader: Reader, stop_marks: Stack) -> Optional[BSeparator]:
    if reader.pull('\n'):
        return BSeparator()

    return None


def parse_title(reader: Reader, stop_marks: Stack) -> Optional[BTitle]:
    if not reader.pull('='):
        return None

    level = 1

    while reader.pull('='):
        level += 1

    while reader.pull(' '):
        pass

    reader.push_indent(reader.column)

    content = parse_block(reader, stop_marks)

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

    content = parse_block(reader, stop_marks)

    reader.pop_indent()

    return BListItem(content, ordered)


def parse_element(reader: Reader, stop_marks: Stack) -> Optional[BElement]:
    if not reader.any('>', '<'):
        return None

    mark = reader.read_char()

    while reader.pull(' '):
        pass

    reader.push_indent(reader.column)

    content = parse_block(reader, stop_marks)

    reader.pop_indent()

    return BElement(content, mark)


def parse_table_row(
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

    content = parse_block(reader, stop_marks)

    reader.pop_indent()
    stop_marks.pop()

    return BTableCell(content)


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


def parse_attribute(reader: Reader, stop_marks: Stack):
    if not reader.pull('@'):
        return None

    name = ''

    while reader.any(*f'_{string.ascii_letters}{string.digits}'):
        name += reader.read_char()

    reader.expect('[')

    value = ''

    while not reader.pull(']'):
        c = reader.read_char()

        if c is None:
            raise Exception('Expected ]')

        value += c

    return BAttribute(name, value)


def parse_line_text(
        reader: Reader, stop_marks: Stack) -> Optional[BLineText]:
    content = []

    while True:
        if reader.test(stop_marks.peek()):
            break

        c = reader.read_char()

        if c is None or c == '\n':
            break

        content += c

    if len(content) == 0:
        return None

    return BLineText(''.join(content))
