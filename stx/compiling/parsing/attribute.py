from abc import ABC

from stx.compiling.parsing.abstract import AbstractParser
from stx.compiling.reading.location import Location
from stx.data_notation.parsing import parse_entry


class AttributeParser(AbstractParser, ABC):

    def parse_attribute(self, location: Location):
        content = self.get_content()

        entry = parse_entry(content)

        content.expect_end_of_line()

        self.composer.push_attribute(entry.name, entry.value)
