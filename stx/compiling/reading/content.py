import re
from collections import namedtuple
from io import StringIO
from typing import List, Optional

from stx.compiling.marks import get_matching_mark
from stx.utils.stx_error import StxError

LF_CHAR = '\n'  # Line Feed

EMPTY_OR_WHITESPACE = r'^ *$'


class TRX:

    def __init__(self, pos: int, line: int, column: int, state: Optional[str]):
        self.pos = pos
        self.line = line
        self.column = column
        self.state = state


class Content:

    def __init__(self, file_path: str):
        self._file_path = file_path
        self._pos = 0
        self._line = 0
        self._column = 0
        self._trx = []

        with open(self._file_path, mode='r') as stream:
            self._content = stream.read()
            self._length = len(self._content)

    def __enter__(self):
        self._trx.append(TRX(self._pos, self._line, self._column, None))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            raise exc_val
        elif len(self._trx) == 0:
            raise Exception('Corrupted transaction')

        trx = self._trx.pop()

        if trx.state == 'R':
            self._pos = trx.pos
            self._line = trx.line
            self._column = trx.column
        elif trx.state != 'C':
            raise Exception('Unfinished transaction!')

    def commit(self):
        if len(self._trx) == 0:
            raise Exception('No available transaction')
        elif self._trx[-1].state is not None:
            raise Exception('Consumed transaction')

        self._trx[-1].state = 'C'

    def rollback(self):
        if len(self._trx) == 0:
            raise Exception('No available transaction')
        elif self._trx[-1].state is not None:
            raise Exception('Consumed transaction')

        self._trx[-1].state = 'R'

    @property
    def column(self):
        return self._column

    @property
    def line(self):
        return self._line

    @property
    def file_path(self):
        return self._file_path

    def halted(self):
        return self._pos >= self._length and len(self._trx) == 0

    def move_next(self):
        if self._pos < self._length:
            new_line = (self._content[self._pos] == LF_CHAR)

            self._pos += 1

            if new_line:
                self._line += 1
                self._column = 0
            else:
                self._column += 1
        else:
            raise Exception('EOF')

    def peek(self) -> Optional[str]:
        if self._pos < self._length:
            return self._content[self._pos]

        return None

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

    def alive(self, indentation: int) -> bool:  # TRX
        if indentation > 0 and self._column < indentation:
            with self:
                line_prefix = self.read_until(['\n'], max_length=indentation)

                if re.match(EMPTY_OR_WHITESPACE, line_prefix):
                    self.commit()
                    return True
                else:
                    self.rollback()
                    return False

        return self._pos < self._length

    def read_mark(self, stop_char: Optional[str]) -> Optional[str]:  # TRX
        with self:
            token = self.read_until([' ', '\n'], consume_last=False)

            mark = get_matching_mark(token)

            self.rollback()

        if mark is None or (stop_char is not None and mark == stop_char):
            return None

        for i in range(len(mark)):
            self.move_next()

        self.read_while([' '])

        return mark

    def read_text(
            self, indentation: int, stop_char: Optional[str]) -> Optional[str]:
        out = StringIO()
        line_number = 0

        while True:
            with self:
                if stop_char is None:
                    line_text = self.read_until(['\n'], consume_last=True)
                else:
                    line_text = self.read_until(['\n', stop_char])

                    if self.peek() == '\n':
                        self.move_next()

                # The text is complete if the line is empty
                if len(line_text.strip(' \n')) == 0:
                    self.commit()
                    break
                elif line_number == 0:
                    out.write(line_text)
                    self.commit()
                    line_number += 1
                    continue
                elif line_text.startswith(indentation * ' '):
                    out.write(line_text[indentation:])
                    self.commit()
                    line_number += 1
                    continue
                else:
                    self.rollback()
                    break

        return out.getvalue()

    def read_line(self, indentation: int):
        with self:

            line_text = self.read_until(['\n'], consume_last=True)

            # The text is complete if the line is empty
            if len(line_text.strip(' \n')) == 0:
                self.commit()
                return ''
            elif self.column >= indentation:
                self.commit()
                return line_text
            elif line_text.startswith(indentation * ' '):
                self.commit()
                return line_text[indentation:]
            else:
                self.rollback()
                return None

    def expect_char(self, options: List[str]):
        c = self.read_next()

        if c not in options:
            raise StxError(f'Expected any of {options}')

        return c

    def expect_end_of_line(self):
        with self:
            text = self.read_until(['\n'], consume_last=True)

            if len(text.strip()) > 0:
                self.rollback()
                raise StxError('Expected end of line.')

            self.commit()

    def skip_empty_line(self):
        with self:
            text = self.read_until(['\n'], consume_last=True)

            if re.match(EMPTY_OR_WHITESPACE, text):
                self.commit()
            else:
                self.rollback()
