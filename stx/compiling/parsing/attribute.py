from abc import ABC

from stx.compiling.parsing.abstract import AbstractParser
from stx.compiling.reading.location import Location
from stx.data_notation.parsing import parse_entry


class AttributeParser(AbstractParser, ABC):

    def parse_attribute(self, location: Location):
        content = self.get_content()

        entry = parse_entry(content)

        content.expect_end_of_line()

        key = entry.name
        value = entry.value.to_any()  # TODO pass Value objects directly to attributes

        self.composer.push_attribute(key, value)
