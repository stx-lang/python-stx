from __future__ import annotations

import re
from io import StringIO
from typing import List, Iterable, Optional, TextIO

from stx.design.attributes_map import AttributesMap

from stx.utils.strs import crop_text

from ._component import Component
from ..utils.stx_error import StxError


class Composite(Component):

    def __init__(self, components: List[Component]):
        self.components = components

    def __repr__(self):
        return f'Composite<{len(self.components)} component(s)>'

    def write_text(self, output: TextIO):
        for component in self.components:
            component.write_text(output)

    def get_children(self) -> List[Component]:
        return self.components

    def pop_attributes(self, attributes: dict):
        raise StxError('not implemented')