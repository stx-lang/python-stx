from __future__ import annotations

import re
from io import StringIO
from typing import List, Iterable, Optional, TextIO

from stx.design.attributes_map import AttributesMap

from stx.utils.strs import crop_text

from ._component import Component
from ..utils.stx_error import StxError


class TextBlock(Component):

    def __init__(self, components: List[Component]):
        self.components = components

    def __repr__(self):
        return f'TextBlock<{crop_text(self.get_text(), 10)}>'

    def write_text(self, output: TextIO):
        for component in self.components:
            component.write_text(output)

    def get_children(self) -> List[Component]:
        return self.components
