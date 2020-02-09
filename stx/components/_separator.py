from __future__ import annotations

import re
from io import StringIO
from typing import List, Iterable, Optional, TextIO

from stx.design.attributes_map import AttributesMap

from stx.utils.strs import crop_text

from ._component import Component
from ..utils.stx_error import StxError


class Separator(Component):

    def __init__(self):
        self.level = 0

    def __repr__(self):
        return f'Separator<{self.level}>'

    def write_text(self, output: TextIO):
        pass

    def get_children(self) -> List[Component]:
        return []

    def pop_attributes(self, attributes: dict):
        raise StxError('not implemented')