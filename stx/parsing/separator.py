import string

from typing import Optional, Tuple, List

from stx.reader import Reader
from stx.utils import Stack
from stx.components.blocks import Block, BComposite, BTitle, BListItem, \
    BElement, BDirective
from stx.components.blocks import BLineText, BSeparator, BTableCell
from stx.components.blocks import BAttribute, BTableRow, BCodeBlock




def parse_separator(
        reader: Reader, stop_marks: Stack) -> Optional[BSeparator]:
    if reader.pull('\n'):
        return BSeparator()

    return None