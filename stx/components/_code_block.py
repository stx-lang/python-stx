from __future__ import annotations

import re
from io import StringIO
from typing import List, Iterable, Optional, TextIO

from stx.design.attributes_map import AttributesMap

from stx.utils.strs import crop_text

from ._component import Component


class CodeBlock(Component):

    def __init__(self, content: str, lang):
        self.content = content
        self.lang = lang

    def __repr__(self):
        return f'CodeBlock<{crop_text(self.content, 10)}>'

    def write_text(self, output: TextIO):
        output.write(self.content)

    def get_children(self) -> List[Component]:
        return []
