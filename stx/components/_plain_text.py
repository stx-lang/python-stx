from __future__ import annotations

import re
from io import StringIO
from typing import List, Iterable, Optional, TextIO

from stx.design.attributes_map import AttributesMap

from stx.utils.strs import crop_text

from ._component import Component
from ..utils.stx_error import StxError


class PlainText(Component):

    def __init__(self, text: str):
        self.text = text

    def __repr__(self):
        return f'PlainText<{crop_text(self.text, 10)}>'

    def write_text(self, output: TextIO):
        output.write(self.text)

    def get_children(self) -> List[Component]:
        return []

    def pop_attributes(self, attributes: dict):
        # TODO implement refs in a global way
        attributes.pop('ref', None)

