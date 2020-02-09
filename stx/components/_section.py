from __future__ import annotations

import re
from io import StringIO
from typing import List, Iterable, Optional, TextIO

from stx.design.attributes_map import AttributesMap

from stx.utils.strs import crop_text

from ._component import Component


class Section(Component):

    def __init__(self, heading: Component, content: Component, level: int):
        self.heading = heading
        self.content = content
        self.level = level
        self.type = None

    def __repr__(self):
        return f'Section<{len(self.components)} component(s)>'

    def write_text(self, output: TextIO):
        self.heading.write_text(output)

        for component in self.components:
            component.write_text(output)

    def get_children(self) -> List[Component]:
        return [self.heading, *self.components]

    def pop_attributes(self, attributes: dict):
        section_id = attributes.pop('id', None)
        section_id = attributes.pop('ref', None)

        # TODO handle IDS & refs
