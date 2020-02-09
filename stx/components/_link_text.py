from __future__ import annotations

import re
from io import StringIO
from typing import List, Iterable, Optional, TextIO

from stx.design.attributes_map import AttributesMap

from stx.utils.strs import crop_text

from ._component import Component
from ..utils.stx_error import StxError


class LinkText(Component):

    def __init__(self, contents: List[Component], reference: Optional[str]):
        self.contents = contents
        self.reference = reference

    def __repr__(self):
        return f'LinkText<{crop_text(self.get_text(), 10)}>'

    def write_text(self, output: TextIO):
        for content in self.contents:
            content.write_text(output)

    def get_children(self) -> List[Component]:
        return self.contents

    @property
    def internal(self) -> bool:
        # TODO refactor to external
        return self.reference is not None and not re.match(r'(?i)^([a-z]+:)?//', self.reference)

    def pop_attributes(self, attributes: dict):
        raise StxError('not implemented')