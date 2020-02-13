from abc import ABC

from stx.compiling.reading.location import Location
from stx.components import ContentBox
from stx.compiling.parsing.abstract import AbstractParser


class ContentBoxParser(AbstractParser, ABC):

    def parse_content_box(
            self,
            location: Location,
            mark_indentation: int):
        box = ContentBox(location)

        self.composer.add(box)

        box.content = self.capture_component(mark_indentation, True)
