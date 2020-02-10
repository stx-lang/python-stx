from typing import List

from stx.components import Section
from stx.parsing3.parsers.base import BaseParser


class SectionParser(BaseParser):

    def parse_section(
            self,
            level: int,
            mark_indentation: int,
            root_indentation: int):
        section = Section(None, None, level)

        self.composer.add(section)

        self.section_stack.append(section)

        section.heading = self.capture_component(
            mark_indentation)
        section.content = self.capture_component(
            root_indentation)

        self.section_stack.pop()
