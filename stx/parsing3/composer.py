from typing import List, Any, Optional

from stx.components import Component, Composite, Figure, Table
from stx.utils.stx_error import StxError


class Composer:

    def __init__(self):
        self.stack: List[List[Component]] = []
        self.attributes_buffer = {}
        self.pre_captions = []

    def push(self):
        self.stack.append([])

    def pop(self) -> Component:
        components = self.stack.pop()

        # TODO add case for len(result) == 0 ?

        if len(components) == 1:
            return components[0]

        return Composite(components)

    @property
    def components(self) -> List[Component]:
        if len(self.stack) == 0:
            raise StxError('Empty stack.')

        return self.stack[-1]

    def add(self, component: Component):
        if len(self.attributes_buffer) > 0:
            component.pop_attributes(self.attributes_buffer)

            if len(self.attributes_buffer) > 0:
                keys = ','.join(self.attributes_buffer.keys())
                raise StxError(f'Unknown attributes {keys}'
                                f' for {type(component)}')

        if len(self.pre_captions) > 0:
            if isinstance(component, Table):
                component.caption = self.pre_captions.pop()
            else:
                figure = Figure(component, self.pre_captions.pop())

                self.components.append(figure)
        else:
            self.components.append(component)

    def push_attribute(self, key: str, value: Any):
        if key in self.attributes_buffer:
            raise StxError(f'Attribute already defined: {key}')

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
            figure = Figure(component, caption)

            comps[-1] = figure
