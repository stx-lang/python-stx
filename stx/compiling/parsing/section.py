from abc import ABC
from typing import List

from stx.components import Section
from stx.compiling.parsing.abstract import AbstractParser


class SectionParser(AbstractParser, ABC):

    def parse_section(
            self,
            level: int,
            mark_indentation: int,
            root_indentation: int):
        section = Section(None, None, level)

        self.composer.add(section)

        self.section_stack.append(section)

        section.heading = self.capture_component(mark_indentation, True)
        section.content = self.capture_component(root_indentation, True)

        self.section_stack.pop()
