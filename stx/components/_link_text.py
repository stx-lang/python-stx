from __future__ import annotations

import re
from typing import List, Optional, TextIO

from ._component import Component, DisplayMode
from ..compiling.reading.location import Location
from ..data_notation.values import Value
from ..utils.tracked_dict import TrackedDict


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
        self.invalid = False

    @property
    def display_mode(self) -> DisplayMode:
        return DisplayMode.INLINE

    def is_rich(self) -> bool:
        return True

    def write_text(self, output: TextIO):
        for content in self.contents:
            content.write_text(output)

    def get_children(self) -> List[Component]:
        return self.contents

    def apply_advanced_attributes(self, attributes: TrackedDict[str, Value]):
        pass

    def is_internal(self) -> bool:
        return self.reference is not None and not is_url(self.reference)

    def is_external(self) -> bool:
        return self.reference is not None and is_url(self.reference)
