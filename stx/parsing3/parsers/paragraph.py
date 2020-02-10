from stx.components import PlainText
from stx.parsing3.parsers.base import BaseParser


class ParagraphParser(BaseParser):

    def parse_paragraph(self, text: str):
        self.composer.add(PlainText(text))  # TODO parse styled text
