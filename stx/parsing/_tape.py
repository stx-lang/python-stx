from __future__ import annotations

from typing import Optional

from ._source import Source


class Tape:

    def __init__(self, source: Source):
        self.source = source

    def _read(self, move: bool) -> Optional[str]:
        line = self.source.try_line()

        if line is not None:
            if line.is_empty:
                self.source.flush_line()
                return None
            elif line.indentation >= line.raw_length:
                self.source.flush_line()
                line = self.source.try_line()

        if line is None:
            return None

        text = line.get_current_text()

        if move:
            line.indentation += 1

        if len(text) == 0:
            return None

        return text[0]

    def skip(self, targets: str) -> int:
        count = 0

        while True:
            c = self._read(False)

            if c is None or c not in targets:
                break

            self._read(True)

            count += 1

        return count

    def peek(self) -> str:
        c = self._read(False)

        if c is None:
            raise self.source.error('Expected to read a char.')

        return c

    def read(self) -> str:
        return self._read(True)

    def alive(self) -> bool:
        return self._read(False) is not None

    def test(self, expected: str) -> bool:
        if expected is None:
            return False

        actual = self._read(False)

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

    @property
    def column_index(self) -> int:
        line = self.source.try_line()

        if line is None:
            return 0

        return line.indentation

