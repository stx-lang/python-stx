from abc import ABC, abstractmethod
from typing import List

from stx.compiling.reading.location import Location
from stx.components import Component, Section
from stx.document import Document
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
    def parse_attribute(self, location: Location):
        pass

    @abstractmethod
    def parse_pre_caption(
            self, location: Location, mark_indentation: int):
        pass

    @abstractmethod
    def parse_post_caption(self, location: Location, indentation: int):
        pass

    @abstractmethod
    def parse_code_block(self, location: Location, root_indentation: int):
        pass

    @abstractmethod
    def parse_content_box(
            self, location: Location, mark_indentation: int):
        pass

    @abstractmethod
    def parse_directive(self, location: Location):
        pass

    @abstractmethod
    def parse_list_item(
            self, location: Location, indentation: int, ordered: bool):
        pass

    @abstractmethod
    def parse_paragraph(self, location: Location, text: str):
        pass

    @abstractmethod
    def parse_section(
            self, location: Location, level: int,
            mark_indentation: int, root_indentation: int):
        pass

    @abstractmethod
    def parse_table_row(
            self, location: Location, indentation: int, header: bool):
        pass

    @abstractmethod
    def parse_table_cell(self, location: Location, indentation: int):
        pass
