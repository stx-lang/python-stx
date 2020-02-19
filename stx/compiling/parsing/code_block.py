from abc import ABC
from io import StringIO

from stx.compiling.reading.location import Location
from stx.components import CodeBlock
from stx.compiling.marks import code_block_mark
from stx.compiling.parsing.abstract import AbstractParser
from stx.data_notation.parsing import try_parse_text
from stx.utils.stx_error import StxError


class CodeBlockParser(AbstractParser, ABC):

    def parse_code_block(
            self,
            location: Location,
            root_indentation: int):
        content = self.get_content()

        lang = try_parse_text(content)

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

        self.composer.add(
            CodeBlock(location, code, lang)
        )
