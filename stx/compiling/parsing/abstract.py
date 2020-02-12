from abc import ABC, abstractmethod
from typing import List

from stx.components import Component, Section
from stx.design.document import Document
from stx.compiling.composer import Composer
from stx.compiling.reading.reader import Reader


class AbstractParser(Reader, ABC):

    def __init__(self, document: Document):
        super().__init__()
        self.document = document
        self.composer = Composer()
        self.stop_mark = None  # TODO Rename to `stop_char`
        self.section_stack: List[Section] = []

    @abstractmethod
    def capture_component(
            self, indentation: int, breakable: bool) -> Component:
        pass

    @abstractmethod
    def capture(self):
        pass

    @abstractmethod
    def parse_components(self, indentation: int, breakable: bool):
        pass

    @abstractmethod
    def parse_attribute(self):
        pass

    @abstractmethod
    def parse_pre_caption(self, mark_indentation: int):
        pass

    @abstractmethod
    def parse_post_caption(self, indentation: int):
        pass

    @abstractmethod
    def parse_code_block(self, root_indentation: int):
        pass

    @abstractmethod
    def parse_content_box(self, mark_indentation: int):
        pass

    @abstractmethod
    def parse_directive(self):
        pass

    @abstractmethod
    def parse_list_item(self, indentation: int, ordered: bool):
        pass

    @abstractmethod
    def parse_paragraph(self, text: str):
        pass

    @abstractmethod
    def parse_section(
            self, level: int, mark_indentation: int, root_indentation: int):
        pass

    @abstractmethod
    def parse_table_row(self, indentation: int, header: bool):
        pass

    @abstractmethod
    def parse_table_cell(self, indentation: int):
        pass
