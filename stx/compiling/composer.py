from typing import List, Any, Optional

from stx.compiling.reading.location import Location
from stx.components import Component, Composite, Figure, Table
from stx.utils.stx_error import StxError
from stx.utils.debug import see

class Composer:

    def __init__(self):
        self.stack: List[List[Component]] = []
        self.attributes_buffer = {}
        self.pre_captions = []

    def push(self):
        self.stack.append([])

    def pop(self) -> Optional[Component]:
        components = self.stack.pop()

        if len(components) == 0:
            return None
        elif len(components) == 1:
            return components[0]

        return Composite(components[0].location, components)

    @property
    def components(self) -> List[Component]:
        if len(self.stack) == 0:
            raise StxError('Empty stack.')

        return self.stack[-1]

    def add(self, component: Component):
        if len(self.attributes_buffer) > 0:
            component.apply_attributes(self.attributes_buffer)
            self.attributes_buffer.clear()

        if len(self.pre_captions) > 0:
            if isinstance(component, Table):
                component.caption = self.pre_captions.pop()
            else:
                figure = Figure(
                    component.location, component, self.pre_captions.pop())

                self.components.append(figure)
        else:
            self.components.append(component)

    def push_attribute(self, key: str, value: Any):
        if key in self.attributes_buffer:
            raise StxError(f'The attribute {see(key)} was already defined.')

        self.attributes_buffer[key] = value

    def get_last_component(self) -> Optional[Component]:
        comps = self.components

        if len(comps) == 0:
            return None

        return comps[-1]

    def push_pre_caption(self, caption: Component):
        self.pre_captions.append(caption)

    def push_post_caption(self, caption: Component):
        comps = self.components

        if len(comps) == 0:
            raise StxError('Expected component for post-caption.')

        component = comps[-1]

        if isinstance(component, Table):
            component.caption = caption
        else:
            figure = Figure(component.location, component, caption)

            comps[-1] = figure
