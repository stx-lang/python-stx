from __future__ import annotations

from typing import Optional, List

from stx.design.attributes_map import AttributesMap
from stx.design.components import Component, Table, Figure


class Composer:

    def __init__(self):
        self.attributes = AttributesMap()
        self.contents: List[Optional[Component]] = []
        self.pending_caption: Optional[Component] = None

    def consume_attributes(self, component: Component):
        component.attributes.update(self.attributes)
        self.attributes.clear()

    def consume_caption(self, component: Component):
        if self.pending_caption is not None:
            if isinstance(component, Table):
                component.caption = self.pending_caption
            else:
                component = Figure(component, self.pending_caption)

            self.pending_caption = None

        return component

    def push(self, content: Component):
        content = self.consume_caption(content)

        self.consume_attributes(content)

        self.contents.append(content)

    def pop(self) -> Component:
        if len(self.contents) == 0:
            raise Exception('Expected content')

        return self.contents.pop()

    def compile(self) -> List[Component]:
        if self.pending_caption is not None:
            raise Exception('pending cation')
        elif len(self.attributes) > 0:
            raise Exception('floating attributes')

        return [c for c in self.contents if c is not None]

    def get_last_content(self) -> Optional[Component]:
        if len(self.contents) == 0:
            return None

        return self.contents[-1]

    def push_separator(self):
        self.contents.append(None)

    def push_attribute(self, name: str, values: List[str]):
        self.attributes.add_values(name, values)


