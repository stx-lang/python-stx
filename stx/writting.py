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

    def write(self, chars: str):
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


class HtmlWriter(Writer):

    def _write_attributes(self, attributes: Optional[dict]):
        if attributes is not None and len(attributes) > 0:
            for attr_name, attr_value in attributes.items():
                self.write(' ')
                self.write(attr_name)  # TODO escape
                self.write('=')
                self.write('"')
                self.write(attr_value)  # TODO escape
                self.write('"')

    def tag(
            self,
            name: str,
            attributes: Optional[dict] = None):
        self.write('<')
        self.write(name)  # TODO escape

        self._write_attributes(attributes)

        self.write('>')

    def open_tag(
            self,
            name: str,
            attributes: Optional[dict] = None):
        self.write('<')
        self.write(name)  # TODO escape

        self._write_attributes(attributes)

        self.write('>\n')
        self.indentation += 1

    def close_tag(self, name: str):
        self.indentation -= 1

        self.break_line()

        self.write('</')
        self.write(name)
        self.write('>\n')

    def text(self, content: str):
        self.write(content)  # TODO escape
