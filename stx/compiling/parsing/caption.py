from abc import ABC

from stx.compiling.parsing.abstract import AbstractParser
from stx.compiling.reading.location import Location


class CaptionParser(AbstractParser, ABC):

    def parse_pre_caption(
            self,
            location: Location,
            mark_indentation: int):
        caption = self.capture_component(mark_indentation, True)

        self.composer.push_pre_caption(caption)

    def parse_post_caption(
            self,
            location: Location,
            indentation: int):
        caption = self.capture_component(indentation, True)

        self.composer.push_post_caption(caption)
