import string

from typing import Optional, Tuple, List

from stx.reader import Reader
from stx.utils import Stack
from stx.components.blocks import Block, BComposite, BTitle, BListItem, \
    BElement, BDirective
from stx.components.blocks import BLineText, BSeparator, BTableCell
from stx.components.blocks import BAttribute, BTableRow, BCodeBlock


import stx.parsing.separator as separator
import stx.parsing.line as line
import stx.parsing.table as table
import stx.parsing.code as code
import stx.parsing.directive as directive
import stx.parsing.element as element


def parse_block(reader: Reader, stop_marks: Stack) -> Block:
    components = []

    while True:
        if reader.test(stop_marks.peek()):
            break

        component = (separator.parse_separator(reader, stop_marks) or
                     element.parse_title(reader, stop_marks) or
                     element.parse_list(reader, stop_marks) or
                     element.parse_element(reader, stop_marks) or
                     table.parse_table_row(reader, stop_marks) or
                     code.parse_code_block(reader, stop_marks) or
                     code.parse_ignore_block(reader, stop_marks) or
                     directive.parse_attribute(reader, stop_marks) or
                     directive.parse_directive(reader, stop_marks) or
                     line.parse_line_text(reader, stop_marks))

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


