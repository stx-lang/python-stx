from typing import Optional

from stx.components.blocks import BLineText
from stx.reader import Reader
from stx.utils import Stack


def parse(
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
