from __future__ import annotations

from typing import List, TextIO

from ._component import Component
from ..compiling.reading.location import Location


class CodeBlock(Component):

    def __init__(self, location: Location, content: str, lang: str):
        self.location = location
        self.content = content
        self.lang = lang

    def write_text(self, output: TextIO):
        output.write(self.content)

    def get_children(self) -> List[Component]:
        return []
