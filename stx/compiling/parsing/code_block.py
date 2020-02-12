from abc import ABC
from io import StringIO

from stx.components import PlainText, CodeBlock
from stx.compiling.marks import code_block_mark
from stx.compiling.parsing.abstract import AbstractParser
from stx.compiling.values import parse_name, NAME_BEGIN_CHARS
from stx.utils.stx_error import StxError


class CodeBlockParser(AbstractParser, ABC):

    def parse_code_block(
            self,
            root_indentation: int):
        content = self.get_content()

        c = content.peek()

        if c in NAME_BEGIN_CHARS:
            lang = parse_name(content)
        else:
            lang = None

        content.expect_end_of_line()

        out = StringIO()

        while True:
            line = content.read_line(root_indentation)

            if line is None:
                raise StxError('Unexpected end of block.')
            elif line.strip() == code_block_mark:
                break

            out.write(line)

        code = out.getvalue()

        self.composer.add(CodeBlock(code, lang))
