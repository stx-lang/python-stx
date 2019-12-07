import string

from typing import Optional

from stx.components.blocks import Block, Content, Title, ListItem, TableRow
from stx.components.blocks import LineText, Separator, TableCell, CodeBlock
from stx.components.blocks import Attribute
from stx.reader import Reader
from stx.utils import Stack


def parse_content(reader: Reader, stop_marks: Stack) -> Block:
    components = []

    while True:
        if reader.test(stop_marks.peek()):
            break

        component = (parse_separator(reader, stop_marks) or
                     parse_title(reader, stop_marks) or
                     parse_list(reader, stop_marks) or
                     parse_table_row(reader, stop_marks) or
                     parse_code_block(reader, stop_marks) or
                     parse_ignore_block(reader, stop_marks) or
                     parse_attribute(reader, stop_marks) or
                     parse_line_text(reader, stop_marks))

        if component is None:
            break
        elif (len(components) > 0
              and isinstance(components[-1], Separator)
              and isinstance(component, Separator)):
            # Collapse multiple separators into one
            components[-1].size += 1
        else:
            components.append(component)

    if len(components) == 0:
        return Separator()
    if len(components) == 1:
        return components[0]

    return Content(components)


def parse_separator(reader: Reader, stop_marks: Stack) -> Optional[Separator]:
    if reader.pull('\n'):
        return Separator()

    return None


def parse_title(reader: Reader, stop_marks: Stack) -> Optional[Title]:
    if not reader.pull('='):
        return None

    level = 1

    while reader.pull('='):
        level += 1

    while reader.pull(' '):
        pass

    reader.push_indent(reader.column)

    content = parse_content(reader, stop_marks)

    reader.pop_indent()

    return Title(content, level)


def parse_list(reader: Reader, stop_marks: Stack) -> Optional[ListItem]:
    if reader.pull('-'):
        ordered = False
    elif reader.pull('.'):
        ordered = True
    else:
        return None

    while reader.pull(' '):
        pass

    reader.push_indent(reader.column)

    content = parse_content(reader, stop_marks)

    reader.pop_indent()

    return ListItem(content, ordered)


def parse_table_row(reader: Reader, stop_marks: Stack) -> Optional[TableRow]:
    cells = []

    while True:
        cell = parse_table_cell(reader, stop_marks)

        if cell is None:
            break

        if isinstance(cell.content, Separator):
            break

        cells.append(cell)

    if len(cells) == 0:
        return None

    return TableRow(cells)


def parse_table_cell(reader: Reader, stop_marks: Stack) -> Optional[TableCell]:
    if not reader.pull('|'):
        return None

    while reader.pull(' '):
        pass

    if reader.test('|'):
        return TableCell(LineText(''))

    stop_marks.push('|')
    reader.push_indent(reader.column)

    content = parse_content(reader, stop_marks)

    reader.pop_indent()
    stop_marks.pop()

    return TableCell(content)


def parse_code_block(reader: Reader, stop_marks: Stack) -> Optional[CodeBlock]:
    content = parse_text_block(reader, '```')

    if content is None:
        return None

    return CodeBlock(content)


def parse_ignore_block(
        reader: Reader,
        stop_marks: Stack) -> Optional[Block]:
    content = parse_text_block(reader, '!!!')

    if content is None:
        return None

    return Separator()


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

    return Attribute(name, value)


def parse_line_text(reader: Reader, stop_marks: Stack) -> Optional[LineText]:
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

    return LineText(''.join(content))
