from __future__ import annotations

import re
from io import StringIO
from typing import List, Iterable, Optional, TextIO

from stx.design.attributes_map import AttributesMap

from stx.utils.strs import crop_text

from ._component import Component
from ..utils.stx_error import StxError


class Heading(Component):

    def __init__(self, content: Component, level: int):
        self.content = content
        self.level = level
        self.number = None

    def __repr__(self):
        return f'Heading<{crop_text(self.get_text(), 10)}>'

    def write_text(self, output: TextIO):
        self.content.write_text(output)

    def get_children(self) -> List[Component]:
        return [self.content]

    def pop_attributes(self, attributes: dict):
        raise StxError('not implemented')
