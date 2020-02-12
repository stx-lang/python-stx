from __future__ import annotations

import re
from io import StringIO
from typing import List, Iterable, Optional, TextIO

from stx.design.attributes_map import AttributesMap

from stx.utils.strs import crop_text

from ._component import Component
from ..utils.stx_error import StxError


class Figure(Component):

    def __init__(self, content: Component, caption: Component):
        self.content = content
        self.caption = caption
        self.number = None

    def __repr__(self):
        return f'Figure<{crop_text(self.caption.get_text(), 10)}>'

    def write_text(self, output: TextIO):
        self.caption.write_text(output)
        self.content.write_text(output)

    def get_children(self) -> List[Component]:
        return [self.caption, self.content]
