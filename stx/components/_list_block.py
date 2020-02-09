from __future__ import annotations

import re
from io import StringIO
from typing import List, Iterable, Optional, TextIO

from stx.design.attributes_map import AttributesMap

from stx.utils.strs import crop_text

from ._component import Component
from ..utils.stx_error import StxError


class ListBlock(Component):

    def __init__(self, items: List[Component], ordered: bool):
        self.items = items
        self.ordered = ordered

    def __repr__(self):
        return f'ListBlock<{len(self.items)} item(s)>'

    def write_text(self, output: TextIO):
        for item in self.items:
            item.write_text(output)

    def get_children(self) -> List[Component]:
        return self.items

    def pop_attributes(self, attributes: dict):
        raise StxError('not implemented')
