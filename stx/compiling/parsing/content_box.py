from abc import ABC

from stx.components import ContentBox
from stx.compiling.parsing.abstract import AbstractParser


class ContentBoxParser(AbstractParser, ABC):

    def parse_content_box(
            self,
            mark_indentation: int):
        box = ContentBox(None)  # TODO make empty constructors

        self.composer.add(box)

        box.content = self.capture_component(mark_indentation, True)
