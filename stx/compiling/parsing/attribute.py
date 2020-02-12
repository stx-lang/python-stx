from abc import ABC

from stx.compiling.parsing.abstract import AbstractParser
from stx.compiling.values import parse_entry


class AttributeParser(AbstractParser, ABC):

    def parse_attribute(self):
        content = self.get_content()

        key, value = parse_entry(content)

        content.expect_end_of_line()
        content.skip_empty_line()

        self.composer.push_attribute(key, value)
