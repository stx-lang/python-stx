from typing import Optional

from stx.components.blocks import BSeparator
from stx.reader import Reader
from stx.utils import Stack


def parse(
        reader: Reader, stop_marks: Stack) -> Optional[BSeparator]:
    if reader.pull('\n'):
        return BSeparator()

    return None