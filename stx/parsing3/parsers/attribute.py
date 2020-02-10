from stx.parsing3.parsers.base import BaseParser
from stx.parsing3.values import parse_entry


class AttributeParser(BaseParser):

    def parse_attribute(self):
        key, value = parse_entry(self.source)

        self.source.expect_end_of_line()
        self.source.skip_empty_line()

        self.composer.push_attribute(key, value)
