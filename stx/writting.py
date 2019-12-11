import string
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


def html_escape_char(c: str) -> str:
    if c not in (string.ascii_letters + string.digits + ' \n.,-/()[]'):
        code = ord(c)

        return f'&#{code};'

    return c


def html_escape(content: str) -> str:
    return ''.join([html_escape_char(c) for c in content])


class HtmlWriter(Writer):

    def _write_attributes(self, attributes: Optional[dict]):
        if attributes is not None and len(attributes) > 0:
            for attr_name, attr_value in attributes.items():
                self.write(' ')
                self.write(html_escape(attr_name))
                self.write('=')
                self.write('"')
                self.write(html_escape(attr_value))
                self.write('"')

    def tag(
            self,
            name: str,
            attributes: Optional[dict] = None,
            inline=False):
        self.write('<')
        self.write(html_escape(name))

        self._write_attributes(attributes)

        self.write('>')

        if not inline:
            self.write('\n')

    def open_tag(
            self,
            name: str,
            attributes: Optional[dict] = None,
            inline=False):
        self.write('<')
        self.write(html_escape(name))

        self._write_attributes(attributes)

        self.write('>')

        if not inline:
            self.write('\n')
            self.indentation += 1

    def close_tag(self, name: str, inline=False):
        if not inline:
            self.indentation -= 1

            self.break_line()

        self.write('</')
        self.write(name)
        self.write('>')

        if not inline:
            self.write('\n')

    def text(self, content: str, disable_indentation=False):
        indentation0 = self.indentation

        if disable_indentation:
            self.indentation = 0

        self.write(html_escape(content))

        if disable_indentation:
            self.indentation = indentation0

    def comment(self, content: str):
        self.break_line()
        self.write('<!--')
        self.text(content)
        self.write('-->\n')
