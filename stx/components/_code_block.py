from __future__ import annotations

import re
from io import StringIO
from typing import List, Iterable, Optional, TextIO

from stx.design.attributes_map import AttributesMap

from stx.utils.strs import crop_text

from ._component import Component


class CodeBlock(Component):

    def __init__(self, code: str, flavor: str):
        self.code = code
        self.flavor = flavor  # TODO rename to lang

    def __repr__(self):
        return f'CodeBlock<{crop_text(self.code, 10)}>'

    def write_text(self, output: TextIO):
        output.write(self.code)

    def get_children(self) -> List[Component]:
        return []

    def pop_attributes(self, attributes: dict):
        self.flavor = attributes.pop('lang')

