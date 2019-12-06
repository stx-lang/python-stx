from typing import List, Optional

ETX = '\u0003'
EOT = '\u0004'


class Reader:

    def __init__(self, content: str):
        self._position = 0
        self.length = len(content)
        self.content = content
        self._indent_stack: List[int] = []

    def debug(self):
        line1 = ''
        line2 = ''

        for i in range(-4, 5):
            p = self.position + i

            if 0 <= p < self.length:
                c = self.content[p]
            else:
                c = '.'

            if c == '\n':
                c = '.'

            line1 += c

            if p == self.position:
                line2 += '^'
            else:
                line2 += ' '

        print(line1)
        print(line2)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value
        self.debug()

    def push_indent(self, indent: int):
        self._indent_stack.append(indent)

    def pop_indent(self):
        self._indent_stack.pop()

    @property
    def indent(self):
        if len(self._indent_stack) > 0:
            return self._indent_stack[-1]

        return 0

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
    def location(self) -> str:
        line = 0
        column = 0

        for i in range(0, self.position):
            if self.content[i] == '\n':
                line += 1
                column = 0
            else:
                column += 1

        return f'{line + 1}:{column + 1}'

    def read_char(self) -> str:
        # EOT if there is nothing to read
        if self.position >= self.length:
            return EOT

        indent = self.indent

        if self.column < indent:
            position0 = self.position
            skipped = 0

            while self.position < self.length and skipped < indent:
                if self.content[self.position] == ' ':
                    self.position += 1
                    skipped += 1
                else:
                    break

            if skipped < indent:
                self.position = position0
                return EOT

        c = self.content[self.position]

        self.position += 1

        if c == '\n':
            position0 = self.position
            separations = 0
            skipped = 0

            while self.position < self.length:
                if self.content[self.position] == ' ':
                    skipped += 1
                elif self.content[self.position] == '\n':
                    position0 = self.position + 1
                    skipped = 0
                    separations += 1

                    if separations > 1:
                        raise Exception(
                            f'{self.location}: Too much separations')
                else:
                    break

                self.position += 1

                if skipped == indent:
                    break

            # EOF If there is no more to read
            if self.position >= self.length:
                return EOT

            # Not enough spaces to complete the indentation, go back
            if skipped < indent:
                self.position = position0
                return EOT

            # ETX If there are separations
            if separations > 0:
                return ETX

        return c

    def test(self, expected: str) -> bool:
        if len(expected) == 0:
            return False
        elif len(expected) > 1:
            raise Exception()

        position0 = self.position

        actual = self.read_char()

        self.position = position0

        return actual == expected

    def any(self, *symbols: str) -> bool:
        for symbol in symbols:
            if self.test(symbol):
                return True

        return False

    def pull(self, expected: str) -> bool:
        if len(expected) == 0:
            return False
        elif len(expected) > 1:
            raise Exception()

        position0 = self.position

        actual = self.read_char()

        if actual != expected:
            self.position = position0
            return False

        return True

    def expect(self, expected: str):
        if not self.pull(expected):
            raise Exception(f'{self.location}: Expected `{expected}`')
