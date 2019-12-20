from __future__ import annotations

from typing import Optional, TextIO, List

from stx.attributes_map import AttributesMap
from stx import marks
from stx.components import Component, Table, Figure


def generate_error_message(message, file_path, line_index, column_index):
    location = ''

    if file_path:
        location += file_path

    if line_index is not None and column_index is not None:
        location += f' @ Line {line_index + 1}, Column {column_index + 1}'
    elif line_index is not None:
        location += f' @ Line {line_index + 1}'
    elif column_index is not None:
        location += f' @ Column {column_index + 1}'

    return f'{location}:\n{message}'


class ParsingError(Exception):

    def __init__(
            self,
            message: str,
            file_path: Optional[str] = None,
            line_index: Optional[int] = None,
            column_index: Optional[int] = None):
        super().__init__(generate_error_message(message, file_path, line_index, column_index))


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

    def error(self, message: str) -> ParsingError:
        return ParsingError(
            message=message,
            file_path=self.file_path,
            line_index=self._next_index - 1,
            column_index=self.peek_begin_index(),
        )


class BlockInfo:

    def __init__(self, mark: str, level: int, begin_index: int):
        self.mark = mark
        self.level = level
        self.begin_index = begin_index


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



    def error(self, message: str, column_index: int) -> ParsingError:
        return ParsingError(
            message=message,
            file_path=self.source.file_path,
            line_index=self.index,
            column_index=column_index,
        )


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

    def error(self, message: str) -> ParsingError:
        return ParsingError(
            message=message,
            file_path=self.source.file_path,
            line_index=self.line_index,
            column_index=self.column_index,
        )


class Composer:

    def __init__(self):
        self.attributes = AttributesMap()
        self.contents: List[Optional[Component]] = []
        self.pending_caption: Optional[Component] = None

    def push(self, content: Component):
        if self.pending_caption is not None:
            if isinstance(content, Table):
                content.caption = self.pending_caption
            else:
                content = Figure(content, self.pending_caption)

            self.pending_caption = None

        # Take buffered attributes
        content.attributes.update(self.attributes)
        self.attributes.clear()

        self.contents.append(content)

    def pop(self) -> Component:
        if len(self.contents) == 0:
            raise Exception('Expected content')

        return self.contents.pop()

    def compile(self) -> List[Component]:
        if self.pending_caption is not None:
            raise Exception('pending cation')

        return [c for c in self.contents if c is not None]

    def get_last_content(self) -> Optional[Component]:
        if len(self.contents) == 0:
            return None

        return self.contents[-1]

    def push_separator(self):  # TODO still valid?
        self.contents.append(None)

    def push_attribute(self, name: str, values: List[str]):
        self.attributes.add_values(name, values)


