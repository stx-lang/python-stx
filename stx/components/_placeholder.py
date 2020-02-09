from __future__ import annotations

import re
from io import StringIO
from typing import List, Iterable, Optional, TextIO

from stx.design.attributes_map import AttributesMap

from stx.utils.strs import crop_text

from ._component import Component


class Placeholder(Component):

    def __init__(self, name: str):
        self.name = name
        self.attrs = None

    def write_text(self, output: TextIO):
        pass

    def get_children(self) -> List[Component]:
        return []

    def __repr__(self):
        return f'Placeholder<{self.name}>'

    def pop_attributes(self, attributes: dict):
        self.attrs = dict(attributes)  # TODO improve attributes handling
        attributes.clear()