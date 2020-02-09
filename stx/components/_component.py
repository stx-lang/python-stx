from __future__ import annotations

import re
from io import StringIO
from typing import List, Iterable, Optional, TextIO

from stx.design.attributes_map import AttributesMap

from stx.utils.strs import crop_text


class Component:
    _attributes = None

    @property
    def attributes(self) -> AttributesMap:
        if self._attributes is None:
            self._attributes = AttributesMap()
        return self._attributes

    def get_text(self) -> str:
        output = StringIO()

        self.write_text(output)

        return output.getvalue()

    def walk(self) -> Iterable[Component]:
        for child in self.get_children():
            yield child

            for c in child.walk():
                yield c

    def write_text(self, output: TextIO):
        raise NotImplementedError()

    def get_children(self) -> List[Component]:
        raise NotImplementedError()

    def __repr__(self):
        raise NotImplementedError()

    def pop_attributes(self, attributes: dict):
        raise NotImplementedError()