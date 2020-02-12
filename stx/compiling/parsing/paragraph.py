from abc import ABC

from stx.components import PlainText
from stx.compiling.parsing.abstract import AbstractParser


class ParagraphParser(AbstractParser, ABC):

    def parse_paragraph(self, text: str):
        self.composer.add(PlainText(text))  # TODO parse styled text
