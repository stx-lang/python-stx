from stx.components import ContentBox
from stx.parsing3.parsers.base import BaseParser


class ContentBoxParser(BaseParser):

    def parse_content_box(
            self,
            mark_indentation: int):
        box = ContentBox(None)  # TODO make empty constructors

        self.composer.add(box)

        box.content = self.capture_component(mark_indentation)
