from __future__ import annotations

import re
from io import StringIO
from typing import List, Optional

from stx import logger
from stx.compiling.marks import get_matching_mark
from stx.compiling.reading.location import Location
from stx.utils.stx_error import StxError
from stx.utils.debug import see

LF_CHAR = '\n'  # Line Feed

EMPTY_OR_WHITESPACE = r'^ *$'


class TRX:

    def __init__(self, content: Content):
        self._content = content
        self._position = None
        self._line = None
        self._column = None
        self._state = 'created'

    def __enter__(self):
        if self._state == 'started':
            raise Exception('Transaction is already started.')

        self._position = self._content.position
        self._line = self._content.line
        self._column = self._content.column
        self._state = 'started'
        self._content.transactions.append(self)
        return self

    def _pop_transaction(self):
        if len(self._content.transactions) == 0:
            raise Exception('Corrupted transaction')

        trx = self._content.transactions.pop()

        if trx != self:
            raise Exception('Corrupted transaction')

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            raise exc_val

        if self._state not in ['saved', 'canceled']:
            raise Exception(f'Unfinished transaction: {self._state}')

    def save(self):
        self._pop_transaction()

        self._state = 'saved'

    def cancel(self):
        self._pop_transaction()

        self._content.position = self._position
        self._content.line = self._line
        self._content.column = self._column

        self._state = 'canceled'


class Content:

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.position = 0
        self.line = 0
        self.column = 0
        self.transactions: List[TRX] = []

        logger.info(f'Loading file {see(file_path, None)}...')

        with open(self.file_path, mode='r') as stream:
            self._content = stream.read().rstrip()
            self._length = len(self._content)

    def checkout(self) -> TRX:
        return TRX(self)

    def go_back(self, location: Location):
        self.position = location.position
        self.line = location.line
        self.column = location.column

    def halted(self):
        return self.position >= self._length and len(self.transactions) == 0

    def move_next(self):
        if self.position < self._length:
            new_line = (self._content[self.position] == LF_CHAR)

            self.position += 1

            if new_line:
                self.line += 1
                self.column = 0
            else:
                self.column += 1
        else:
            raise StxError('EOF')

    def peek(self) -> Optional[str]:
        if self.position < self._length:
            return self._content[self.position]

        return None

    def read_next(self) -> Optional[str]:
        c = self.peek()

        if c is None:
            return None

        self.move_next()
        return c

    def read_until(
            self,
            chars: List[str],
            consume_last=False,
            max_length=None) -> str:
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
        if indentation > 0 and self.column < indentation:
            with self.checkout() as trx:
                line_prefix = self.read_until(['\n'], max_length=indentation)

                if re.match(EMPTY_OR_WHITESPACE, line_prefix):
                    trx.save()
                    return True
                else:
                    trx.cancel()
                    return False

        return self.position < self._length

    def read_mark(self) -> Optional[str]:  # TRX
        with self.checkout() as trx:
            token = self.read_until([' ', '\n'], consume_last=False)

            mark = get_matching_mark(token)

            trx.cancel()

        if mark is None:
            return None

        for i in range(len(mark)):
            self.move_next()

        self.read_while([' '])

        return mark

    def read_line(self, indentation: int):
        with self.checkout() as trx:

            line_text = self.read_until(['\n'], consume_last=True)

            # The text is complete if the line is empty
            if len(line_text.strip(' \n')) == 0:
                trx.save()
                return ''
            elif self.column >= indentation:
                trx.save()
                return line_text
            elif line_text.startswith(indentation * ' '):
                trx.save()
                return line_text[indentation:]
            else:
                trx.cancel()
                return None

    def expect_char(self, options: List[str]):
        c = self.read_next()

        if c not in options:
            raise StxError(f'Expected any of {options}')

        return c

    def expect_end_of_line(self):
        with self.checkout() as trx:
            text = self.read_until(['\n'], consume_last=True)

            if len(text.strip()) > 0:
                trx.cancel()
                raise StxError('Expected end of line.')

            trx.save()

    def get_location(self) -> Location:
        return Location(self.file_path, self.line, self.column, self.position)

    def read_spaces(self, max_length: int = None) -> int:
        count = 0

        while self.peek() == ' ':
            self.move_next()

            count += 1

            if max_length is not None and count >= max_length:
                break

        return count

    def consume_indentation(self, indentation: int) -> bool:
        loc0 = self.get_location()

        while self.column < indentation:
            if self.peek() == ' ':
                self.move_next()
            else:
                break

        if self.column >= indentation:
            return True

        self.go_back(loc0)
        return False

    def consume_empty_line(self) -> bool:
        loc0 = self.get_location()

        count = 0

        while self.peek() == ' ':
            self.move_next()

            count += 1

        c = self.peek()

        if c is None:
            return count > 0
        elif c == '\n':
            self.move_next()
            return True

        self.go_back(loc0)
        return False
