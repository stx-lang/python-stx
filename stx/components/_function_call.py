from __future__ import annotations

from typing import List, TextIO, Optional

from ._component import Component
from ..compiling.reading.location import Location
from ..data_notation.values import Value
from ..utils.tracked_dict import TrackedDict


class FunctionCall(Component):

    def __init__(
            self,
            location: Location,
            inline: bool,
            key: str,
            options: Value,
            content_arg: Optional[Component] = None,
            literal_arg: Optional[str] = None):
        self.location = location
        self.inline = inline
        self.key = key
        self.options = options
        self.content_arg = content_arg
        self.literal_arg = literal_arg
        self.result: Optional[Component] = None

    def write_text(self, output: TextIO):
        if self.result is not None:
            self.result.write_text(output)

    def get_children(self) -> List[Component]:
        if self.result is not None:
            return [self.result]
        return []

    def apply_advanced_attributes(self, attributes: TrackedDict[str, Value]):
        pass
