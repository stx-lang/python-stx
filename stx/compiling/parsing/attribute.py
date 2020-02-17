from abc import ABC

from stx.compiling.parsing.abstract import AbstractParser
from stx.compiling.reading.location import Location
from stx.compiling.values import parse_entry


class AttributeParser(AbstractParser, ABC):

    def parse_attribute(self, location: Location):
        content = self.get_content()

        key, value = parse_entry(content)

        content.expect_end_of_line()

        self.composer.push_attribute(key, value)
