from typing import TextIO, Optional


class Writer:

    def __init__(
            self,
            out: TextIO,
            pretty_print=True,
            tab_symbol: Optional[str] = None):
        self._out = out
        self._broken = False
        self.pretty_print = pretty_print
        self.tab_symbol = tab_symbol or '  '
        self.indentation = 0

    def write_raw(self, chars: Optional[str]):
        if not chars:
            return

        self._out.write(chars)

    def write(self, chars: Optional[str]):
        if not chars:
            return

        for char in chars:
            if self._broken:
                if self.pretty_print and self.indentation > 0:
                    self._out.write(self.indentation * self.tab_symbol)
                self._broken = False

            self._out.write(char)

            if char == '\n':
                self._broken = True

    def break_line(self):
        if not self._broken:
            self.write('\n')
