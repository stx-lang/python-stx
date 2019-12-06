from typing import TextIO, List, Optional, Union


class Tape:

    def __init__(self, content: str):
        self.content = content
        self.position = 0
        self.length = len(content)

    def pull(
            self,
            expected: Optional[str] = None,
            count: Optional[int] = None) -> str:
        if count is None:
            count = len(expected) if expected is not None else 1

        buffer = []

        for i in range(0, count):
            c = self.current

            self.position += 1

            if expected and c != expected[i]:
                raise Exception(
                    f'{self.location}: Expected symbol'
                    f' `{expected[i]}` instead of `{c}`.')

            buffer.append(c)

        return ''.join(buffer)

    def test(self, symbol: str) -> bool:
        if not symbol:
            return False

        for i in range(0, len(symbol)):
            test_sym = symbol[i]
            test_pos = self.position + i
            if test_pos >= self.length or self.content[test_pos] != test_sym:
                return False

        return True

    @property
    def alive(self) -> bool:
        return self.position < self.length

    @property
    def current(self) -> str:
        if self.position >= self.length:
            raise Exception(f'{self.location}: EOF')

        return self.content[self.position]

    @property
    def next(self) -> str:
        if self.position + 1 < self.length:
            return self.content[self.position + 1]
        return ''

    @property
    def previous(self) -> str:
        if self.position <= 0:
            return ''

        return self.content[self.position - 1]

    @property
    def empty_line(self) -> bool:
        return self.previous == '\n' and self.current == '\n'

    @property
    def line(self):
        line = 0
        for i in range(0, self.position):
            if self.content[i] == '\n':
                line += 1

        return line

    @property
    def column(self):
        column = 0
        for i in range(0, self.position):
            if self.content[i] == '\n':
                column = 0
            else:
                column += 1

        return column

    @property
    def location(self):
        return f'{self.line + 1}:{self.column + 1}'
