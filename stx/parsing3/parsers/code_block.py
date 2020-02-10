from io import StringIO

from stx.components import PlainText, CodeBlock
from stx.parsing3.marks import code_block_mark
from stx.parsing3.parsers.base import BaseParser
from stx.parsing3.values import parse_name, NAME_BEGIN_CHARS
from stx.utils.stx_error import StxError


class CodeBlockParser(BaseParser):

    def parse_paragraph(self, text: str):
        self.composer.add(PlainText(text))  # TODO parse styled text

    def parse_code_block(
            self,
            root_indentation: int):
        c = self.source.peek()

        if c in NAME_BEGIN_CHARS:
            lang = parse_name(self.source)
        else:
            lang = None

        self.source.expect_end_of_line()

        out = StringIO()

        while True:
            line = self.source.read_line(root_indentation)

            if line is None:
                raise StxError('Unexpected end of block.')
            elif line.strip() == code_block_mark:
                break

            out.write(line)

        code = out.getvalue()

        self.composer.add(CodeBlock(code, lang))
