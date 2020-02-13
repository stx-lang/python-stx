from __future__ import annotations

import re
from typing import List, Optional, TextIO

from ._component import Component
from ..compiling.reading.location import Location


def is_url(ref: str) -> bool:
    return bool(re.match(r'(?i)^([a-z]+:)?//', ref))


class LinkText(Component):

    def __init__(
            self,
            location: Location,
            contents: List[Component],
            reference: Optional[str]):
        self.location = location
        self.contents = contents
        self.reference = reference

    def write_text(self, output: TextIO):
        for content in self.contents:
            content.write_text(output)

    def get_children(self) -> List[Component]:
        return self.contents

    def is_internal(self) -> bool:
        return self.reference is not None and not is_url(self.reference)

    def is_external(self) -> bool:
        return self.reference is not None and is_url(self.reference)
