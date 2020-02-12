from __future__ import annotations

import re
from io import StringIO
from typing import List, Iterable, Optional, TextIO

from stx.design.attributes_map import AttributesMap

from stx.utils.strs import crop_text

from ._component import Component
from ..utils.stx_error import StxError


class StyledText(Component):

    def __init__(self, contents: List[Component], style: str):
        self.contents = contents
        self.style = style

    def __repr__(self):
        return f'StyledText<{crop_text(self.get_text(), 10)}>'

    def write_text(self, output: TextIO):
        for content in self.contents:
            content.write_text(output)

    def get_children(self) -> List[Component]:
        return self.contents
