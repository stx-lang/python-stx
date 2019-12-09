import string

from typing import Optional, Tuple, List

from stx.reader import Reader
from stx.utils import Stack
from stx.components.blocks import Block, BComposite, BTitle, BListItem, \
    BElement, BDirective
from stx.components.blocks import BLineText, BSeparator, BTableCell
from stx.components.blocks import BAttribute, BTableRow, BCodeBlock


def parse_name_values(reader) -> Tuple[str, List[str]]:
    name = ''

    while reader.any(*f'_{string.ascii_letters}{string.digits}'):
        name += reader.read_char()

    reader.expect('[')

    values = []

    value = ''

    while True:
        c = reader.read_char()

        if c is None:
            raise Exception('Expected ]')

        if c == ']':
            break
        elif c == ',':
            values.append(value.strip())
            value = ''

        value += c

    return name, values


def parse_attribute(reader: Reader, stop_marks: Stack):
    if not reader.pull('@'):
        return None

    name, values = parse_name_values(reader)

    return BAttribute(name, values)


def parse_directive(reader: Reader, stop_marks: Stack):
    if not reader.pull('#'):
        return None

    name, values = parse_name_values(reader)

    return BDirective(name, values)

