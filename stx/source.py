from __future__ import annotations

from typing import Optional, TextIO, List

from stx import marks
from stx.errors import ParseError


class Source:

    def __init__(self, stream: TextIO, file_path: str):
        self._stream = stream
        self.file_path = file_path
        self._begin_index_stack: List[int] = []
        self._curr_line: Optional[Line] = None
        self._next_index = 0

    def try_line(self) -> Optional[Line]:
        if self._curr_line is None:
            if self._stream is None:
                return None

            text = self._stream.readline()

            if text == '':
                self._stream = None
                return None

            text = text.rstrip('\r\n')

            self._curr_line = Line(self, text, self._next_index)
            self._next_index += 1

        if self._curr_line.indentation < self.peek_begin_index() and not self._curr_line.is_empty:
            return None

        return self._curr_line

    def is_alive(self) -> bool:
        return self.try_line() is not None

    def get_line(self) -> Line:
        line = self.try_line()

        if line is None:
            raise self.error('Expected to read a line.')

        return line

    def pop_line(self) -> Line:
        line = self.get_line()

        self._curr_line = None

        return line

    def flush_line(self):
        self._curr_line = None

    def peek_begin_index(self) -> int:
        if len(self._begin_index_stack) == 0:
            return 0

        return self._begin_index_stack[-1]

    def push_begin_index(self, begin_index: int):
        self._begin_index_stack.append(begin_index)

    def pop_begin_index(self):
        self._begin_index_stack.pop()

    def error(self, message: str) -> ParseError:
        return ParseError(
            message=message,
            file_path=self.file_path,
            line_index=self._next_index - 1,
            column_index=self.peek_begin_index(),
        )


class Line:

    def __init__(self, source: Source, raw_text: str, index: int):
        self.source = source
        self.raw_text = raw_text
        self.index = index

        raw_length = len(raw_text)
        indentation = 0

        for c in raw_text:
            if c == ' ':
                indentation += 1
            else:
                break

        self.raw_length = raw_length
        self.is_empty = (indentation == raw_length)
        self.indentation = indentation

    def __repr__(self):
        return f'Line {self.index+1}: {self.raw_text}'

    def get_current_text(self) -> str:
        begin_index = self.source.peek_begin_index()

        if begin_index < self.indentation:
            begin_index = self.indentation

        return self.raw_text[begin_index:]

    def test_current_text(self, expected: str, strip=True) -> bool:
        actual = self.get_current_text()

        if strip:
            actual = actual.strip()

        return actual == expected

    def consume_block_info(self) -> Optional[str]:
        text = self.get_current_text()

        for mark in marks.reserved_block_marks:
            if text.startswith(mark):
                begin_index = self.indentation + len(mark)

                while begin_index < self.raw_length:
                    if self.raw_text[begin_index] == ' ':
                        begin_index += 1
                    else:
                        break

                self.indentation = begin_index

                return mark

        return None

    def error(self, message: str, column_index: int) -> ParseError:
        return ParseError(
            message=message,
            file_path=self.source.file_path,
            line_index=self.index,
            column_index=column_index,
        )
