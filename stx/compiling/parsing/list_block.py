from abc import ABC

from stx.compiling.reading.location import Location
from stx.components import ListBlock
from stx.compiling.parsing.abstract import AbstractParser


class ListBlockParser(AbstractParser, ABC):

    def parse_list_item(
            self,
            location: Location,
            indentation: int,
            ordered: bool):
        list_block = self.composer.get_last_component()

        if not isinstance(list_block, ListBlock):
            list_block = ListBlock(location, ordered)

            self.composer.add(list_block)

        list_item = self.capture_component(indentation, True)

        # TODO ensure that is from the same content
        self.get_content().skip_empty_line()

        list_block.items.append(list_item)
