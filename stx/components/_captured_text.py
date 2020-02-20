from __future__ import annotations

from typing import List, Optional, TextIO

from ._component import Component
from ..compiling.reading.location import Location
from ..data_notation.values import Value
from ..utils.tracked_dict import TrackedDict


class CapturedText(Component):

    def __init__(
            self,
            location: Location,
            contents: List[Component],
            class_: Optional[str]):
        self.location = location
        self.contents = contents
        self.class_ = class_

    def write_text(self, output: TextIO):
        for content in self.contents:
            content.write_text(output)

    def get_children(self) -> List[Component]:
        return self.contents

    def apply_advanced_attributes(self, attributes: TrackedDict[str, Value]):
        pass
