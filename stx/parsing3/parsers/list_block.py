from stx.components import ListBlock
from stx.parsing3.parsers.base import BaseParser


class ListBlockParser(BaseParser):

    def parse_list_item(
            self,
            indentation: int,
            ordered: bool):
        list_block = self.composer.get_last_component()

        if not isinstance(list_block, ListBlock):
            list_block = ListBlock([], ordered)

            self.composer.add(list_block)

        list_item = self.capture_component(indentation)

        list_block.items.append(list_item)

