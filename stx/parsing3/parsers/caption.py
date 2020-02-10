from stx.parsing3.parsers.base import BaseParser


class CaptionParser(BaseParser):

    def parse_pre_caption(
            self,
            mark_indentation: int):
        caption = self.capture_component(mark_indentation)

        self.composer.push_pre_caption(caption)

    def parse_post_caption(
            self,
            indentation: int):
        caption = self.capture_component(indentation)

        self.composer.push_post_caption(caption)
