import string

from typing import Optional, Tuple, List

from stx.reader import Reader
from stx.utils import Stack
from stx.components.blocks import Block, BComposite, BTitle, BListItem, \
    BElement, BDirective
from stx.components.blocks import BLineText, BSeparator, BTableCell
from stx.components.blocks import BAttribute, BTableRow, BCodeBlock



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
