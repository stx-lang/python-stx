from typing import List

from stx.components import Component, Section
from stx.design.document import Document
from stx.parsing3.composer import Composer
from stx.parsing3.source import Source


class BaseParser:

    def __init__(self, document: Document):
        self.document = document
        self.composer = Composer()
        self.source_stack: List[Source] = []
        self.section_stack: List[Section] = []

    @property
    def source(self) -> Source:
        if len(self.source_stack) == 0:
            raise Exception('Not available source')

        return self.source_stack[-1]

    def parse_components(self, indentation: int, breakable=True):
        pass

    def capture_component(
            self,
            indentation: int,
            breakable=True) -> Component:
        self.composer.push()

        self.parse_components(
            indentation,
            breakable)

        return self.composer.pop()

    def capture(self, source: Source):
        self.source_stack.append(source)

        self.document.content = self.capture_component(
            indentation=0,
            breakable=False)

        self.source_stack.pop()