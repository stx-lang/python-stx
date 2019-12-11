from typing import List, Optional

from stx.components.content import CContent, CStyledText, CLinkText, \
    CPlainText, CParagraph
from stx.utils import Stack


class Tape:

    def __init__(self, content: str):
        self.content = content
        self.length = len(content)
        self.position = 0

    def read(self) -> str:
        if self.position >= self.length:
            raise Exception()

        c = self.content[self.position]

        self.position += 1

        return c

    def alive(self):
        return self.position < self.length

    def test(self, c: Optional[str]) -> bool:
        if not c:
            return False
        elif self.position >= self.length:
            return False

        return self.content[self.position] == c

    def any(self, *chars: str) -> bool:
        for c in chars:
            if self.test(c):
                return True
        return False

    def pull(self, c: str) -> bool:
        if self.test(c):
            self.read()
            return True

        return False


def parse_styled_text(tape: Tape, stop_marks: Stack) -> Optional[CStyledText]:
    if tape.test('*'):
        style = 'strong'
    elif tape.test('_'):
        style = 'emphasized'
    elif tape.test('`'):
        style = 'code'
    else:
        return None

    delimiter = tape.read()

    stop_marks.push(delimiter)

    contents = parse_contents(tape, stop_marks)

    stop_marks.pop()

    if not tape.pull(delimiter):
        raise Exception('styled text not closed')

    return CStyledText(contents, style)


def parse_link_text(tape: Tape, stop_marks: Stack) -> Optional[CLinkText]:
    if not tape.pull('['):
        return None

    stop_marks.push(']')

    contents = parse_contents(tape, stop_marks)

    stop_marks.pop()

    if not tape.pull(']'):
        raise Exception('link not closed')

    if tape.pull('('):
        reference = ''

        while not tape.test(')'):
            reference += tape.read()

        if not tape.pull(')'):
            raise Exception('reference not closed')
    else:
        reference = None

    return CLinkText(contents, reference)


def parse_plain_text(tape: Tape, stop_marks: Stack) -> Optional[CPlainText]:
    content = ''

    while tape.alive():
        if tape.test(stop_marks.peek()):
            break
        elif tape.any('*', '_', '`', '['):
            break
        elif tape.pull('\\'):
            if tape.test(stop_marks.peek()):
                content += tape.read()
            elif tape.any('*', '_', '`', '[', ']', '(', ')', '\\'):
                content += tape.read()
            else:
                content += '\\'
        else:
            content += tape.read()

    if len(content) == 0:
        return None

    return CPlainText(content)


def parse_contents(tape: Tape, stop_marks: Stack) -> List[CContent]:
    contents = []

    while tape.alive():
        if tape.test(stop_marks.peek()):
            break

        content = (parse_styled_text(tape, stop_marks)
                   or parse_link_text(tape, stop_marks)
                   or parse_plain_text(tape, stop_marks))

        if content is not None:
            contents.append(content)

    return contents


def compile_paragraph(text: str) -> CParagraph:
    contents = parse_contents(Tape(text), Stack())

    return CParagraph(contents)


def compile_lines(lines: List[str]) -> Optional[CContent]:
    return compile_paragraph('\n'.join(lines))
