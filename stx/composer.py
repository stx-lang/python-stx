from __future__ import annotations

from typing import Optional, List

from stx.attributes_map import AttributesMap
from stx.components import Component, Table, Figure


class Composer:

    def __init__(self):
        self.attributes = AttributesMap()
        self.contents: List[Optional[Component]] = []
        self.pending_caption: Optional[Component] = None

    def push(self, content: Component):
        if self.pending_caption is not None:
            if isinstance(content, Table):
                content.caption = self.pending_caption
            else:
                content = Figure(content, self.pending_caption)

            self.pending_caption = None

        # Take buffered attributes
        content.attributes.update(self.attributes)
        self.attributes.clear()

        self.contents.append(content)

    def pop(self) -> Component:
        if len(self.contents) == 0:
            raise Exception('Expected content')

        return self.contents.pop()

    def compile(self) -> List[Component]:
        if self.pending_caption is not None:
            raise Exception('pending cation')

        return [c for c in self.contents if c is not None]

    def get_last_content(self) -> Optional[Component]:
        if len(self.contents) == 0:
            return None

        return self.contents[-1]

    def push_separator(self):  # TODO still valid?
        self.contents.append(None)

    def push_attribute(self, name: str, values: List[str]):
        self.attributes.add_values(name, values)


