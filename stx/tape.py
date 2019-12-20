from __future__ import annotations

from typing import Optional

from stx.errors import ParseError
from stx.source import Source


class Tape:

    def __init__(self, source: Source):
        self.source = source
        self.text = ''
        self.position = 0
        self.line_index = None
        self.column_index = None

    def skip(self, targets: str) -> int:
        count = 0

        while True:
            c = self.try_peek()

            if c is None or c not in targets:
                break

            count += 1
            self.position += 1
            self.column_index += 1

        return count

    def try_peek(self) -> Optional[str]:
        if self.text is None:
            return None
        elif self.position >= len(self.text):
            line = self.source.try_line()

            if line is None:
                self.text = None
                return None

            self.source.flush_line()

            self.line_index = line.index
            self.column_index = 0

            if line.is_empty:
                self.text = None
                return None

            self.text += line.get_current_text() + '\n'

        return self.text[self.position]

    def peek(self) -> str:
        c = self.try_peek()

        if c is None:
            raise self.error('Expected to read a char.')

        return c

    def read(self) -> str:
        c = self.peek()

        self.position += 1
        self.column_index += 1

        return c

    def alive(self) -> bool:
        return self.try_peek() is not None

    def test(self, expected: str) -> bool:
        if expected is None:
            return False

        actual = self.try_peek()

        if actual is None:
            return False

        return actual in expected

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

    def error(self, message: str) -> ParseError:
        return ParseError(
            message=message,
            file_path=self.source.file_path,
            line_index=self.line_index,
            column_index=self.column_index,
        )

