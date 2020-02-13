from abc import ABC
from io import StringIO
from typing import List, Optional

from stx.compiling.reading.location import Location
from stx.compiling.reading.tape import Tape
from stx.components import PlainText, Component, LinkText, StyledText, \
    Paragraph
from stx.compiling.parsing.abstract import AbstractParser
from stx.utils.stx_error import StxError

ESCAPE_CHAR = '\\'

LINK_BEGIN_CHAR = '['
LINK_END_CHAR = ']'
LINK_REF_BEGIN_CHAR = '('
LINK_REF_END_CHAR = ')'

STYLE_CHAR_TOKEN_MAP = {
    '*': 'strong',
    '_': 'emphasized',
    '`': 'code',
}

BEGIN_CHAR_LIST = [LINK_BEGIN_CHAR] + list(STYLE_CHAR_TOKEN_MAP.keys())


def consume_text(tape: Tape, stop_char: str, greedy: bool) -> str:
    out = StringIO()

    while True:
        c = tape.peek()

        if c is None or c == stop_char or (
                not greedy and c in BEGIN_CHAR_LIST):
            break
        elif c == ESCAPE_CHAR:
            tape.move_next()

            c = tape.peek()

            if c is None:
                raise StxError('expected special char')
            elif c != stop_char and (greedy or c not in BEGIN_CHAR_LIST):
                raise StxError('invalid escaped char')

        out.write(c)
        tape.move_next()

    return out.getvalue()


def parse_contents(
        location: Location,
        tape: Tape,
        stop_char: str) -> List[Component]:
    contents = []

    while True:
        c = tape.peek()

        if c is None or c == stop_char:
            break
        elif c == LINK_BEGIN_CHAR:
            tape.move_next()

            children = parse_contents(location, tape, LINK_END_CHAR)

            if tape.peek() != LINK_END_CHAR:
                raise StxError('Expected link end char')

            tape.move_next()

            if tape.peek() == LINK_REF_BEGIN_CHAR:
                tape.move_next()

                ref = consume_text(tape, LINK_REF_END_CHAR, greedy=True)

                if tape.peek() != LINK_REF_END_CHAR:
                    raise StxError('expected link ref end char')

                tape.move_next()
            else:
                ref = None

            component = LinkText(location, children, ref)  # TODO fix location
        elif c in STYLE_CHAR_TOKEN_MAP:
            tape.move_next()

            token = STYLE_CHAR_TOKEN_MAP[c]
            children = parse_contents(location, tape, c)

            if tape.peek() != c:
                raise StxError(f'Unclosed style: {token}')

            tape.move_next()

            component = StyledText(location, children, token)  # TODO fix location
        else:
            text = consume_text(tape, stop_char, greedy=False)

            component = PlainText(location, text)  # TODO fix location

        contents.append(component)

    return contents


class ParagraphParser(AbstractParser, ABC):

    def parse_paragraph(self, location: Location, text: str):
        tape = Tape(text)
        contents = parse_contents(location, tape, self.stop_mark)

        self.composer.add(Paragraph(location, contents))
