import re
from io import StringIO
from typing import Optional, List

from stx.parsing._marks import get_matching_mark
from stx.utils.stx_error import StxError
from stx.utils.thread_context import context

EMPTY_OR_WHITESPACE = r'^ *$'


class Source:

    @staticmethod
    def from_file(file_path: str):
        with open(file_path, mode='r') as stream:
            content = stream.read()

        return Source(content, file_path)

    def __init__(self, content: str, file_path: str):
        self.content = content
        self.file_path = file_path
        self.length = len(content)
        self.stop_mark = None
        self._pos = 0
        self._line = 0
        self._column = 0
        self._pos_trx = []

    def __enter__(self):
        context.push_source(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        context.pop_source()

    def alive(self, indentation=0) -> bool:
        if indentation > 0 and self._column < indentation:
            self.checkout_position()

            line_prefix = self.read_until(['\n'], max_length=indentation)

            if re.match(EMPTY_OR_WHITESPACE, line_prefix):
                self.commit_position()
                return True
            else:
                self.rollback_position()
                return False

        return self._pos < self.length

    @property
    def column(self) -> int:
        return self._column

    def move_next(self):
        if self._pos < self.length:
            new_line = self.content[self._pos] == '\n'

            self._pos += 1

            if self._pos < self.length and new_line:
                self._line += 1
                self._column = 0
            else:
                self._column += 1

    def peek(self) -> Optional[str]:
        if self._pos >= self.length:
            return None

        return self.content[self._pos]

    def checkout_position(self):
        self._pos_trx.append((self._pos, self._line, self._column))

    def commit_position(self):
        self._pos_trx.pop()

    def rollback_position(self):
        self._pos, self._line, self._column = self._pos_trx.pop()

    def read_next(self) -> Optional[str]:
        c = self.peek()

        if c is None:
            return None

        self.move_next()
        return c

    def read_until(
            self, chars: List[str], consume_last=False, max_length=None) -> str:
        out = StringIO()

        while True:
            if max_length is not None and out.tell() >= max_length:
                break

            c = self.peek()

            if c is None:
                break
            elif c in chars:
                if consume_last:
                    out.write(c)
                    self.move_next()
                break

            out.write(c)
            self.move_next()

        return out.getvalue()

    def read_while(self, chars: List[str]) -> str:
        out = StringIO()

        while True:
            c = self.peek()

            if c is None or c not in chars:
                break

            out.write(c)

            self.move_next()

        return out.getvalue()

    def read_max(self, max_length: int) -> str:
        out = StringIO()

        while True:
            c = self.peek()

            if c is None:
                break

            out.write(c)

            self.move_next()

            if out.tell() >= max_length:
                break

        return out.getvalue()

    def read_mark(self) -> Optional[str]:
        self.checkout_position()

        token = self.read_until([' ', '\n'], consume_last=False)

        mark = get_matching_mark(token)

        self.rollback_position()

        if mark is None or (self.stop_mark is not None
                            and mark == self.stop_mark):
            return None

        for i in range(len(mark)):
            self.move_next()

        return mark

    def read_text(self, indentation: int) -> Optional[str]:
        out = StringIO()
        line_number = 0

        while True:
            self.checkout_position()

            if self.stop_mark is None:
                line_text = self.read_until(['\n'], consume_last=True)
            else:
                line_text = self.read_until(['\n', self.stop_mark])

                if self.peek() == '\n':
                    self.move_next()

            # The text is complete if the line is empty
            if len(line_text.strip(' \n')) == 0:
                self.commit_position()
                break
            elif line_number == 0:
                out.write(line_text)
                self.commit_position()
                line_number += 1
                continue
            elif line_text.startswith(indentation * ' '):
                out.write(line_text[indentation:])
                self.commit_position()
                line_number += 1
                continue
            else:
                self.rollback_position()
                break

        return out.getvalue()

    def read_line(self, indentation: int):
        self.checkout_position()

        line_text = self.read_until(['\n'], consume_last=True)

        # The text is complete if the line is empty
        if len(line_text.strip(' \n')) == 0:
            return ''
        elif self.column >= indentation:
            self.commit_position()
            return line_text
        elif line_text.startswith(indentation * ' '):
            self.commit_position()
            return line_text[indentation:]
        else:
            self.rollback_position()
            return None

    def expect_char(self, options: List[str]):
        c = self.read_next()

        if c not in options:
            raise StxError(f'Expected any of {options}')

        return c

    def expect_end_of_line(self):
        self.checkout_position()

        text = self.read_until(['\n'], consume_last=True)

        if len(text.strip()) > 0:
            self.rollback_position()
            raise StxError('Expected end of line.')

        self.commit_position()

    def skip_empty_line(self):
        self.checkout_position()

        text = self.read_until(['\n'], consume_last=True)

        if re.match(EMPTY_OR_WHITESPACE, text):
            self.commit_position()
        else:
            self.rollback_position()
