from typing import List, Optional

from stx.components import Component, Composite, Figure, Table
from stx.data_notation.values import Value
from stx.utils.stx_error import StxError
from stx.utils.debug import see
from stx.utils.tracked_dict import TrackedDict


class Composer:

    def __init__(self):
        self.stack: List[List[Component]] = []
        self.attributes_buffer: TrackedDict[str, Value] = TrackedDict({})
        self.pre_captions: List[Component] = []

    def push(self):
        self.stack.append([])

    def pop(self) -> Optional[List[Component]]:
        return self.stack.pop()

    @property
    def components(self) -> List[Component]:
        if len(self.stack) == 0:
            raise StxError('Empty stack.')

        return self.stack[-1]

    def add(self, component: Component):
        if not self.attributes_buffer.empty():
            component.apply_attributes(self.attributes_buffer)

            unknown_attr_keys = self.attributes_buffer.unknown_keys()

            if len(unknown_attr_keys) > 0:
                # TODO improve error message
                raise StxError(f'Unknown attributes: {unknown_attr_keys} '
                               f'for {type(component)}.')

            self.attributes_buffer.clear()

        if len(self.pre_captions) > 0:
            if isinstance(component, Table):
                component.caption = self.pre_captions.pop()

                self.components.append(component)
            else:
                figure = Figure(
                    component.location, component, self.pre_captions.pop())

                self.components.append(figure)
        else:
            self.components.append(component)

    def push_attribute(self, key: str, value: Value):
        if key in self.attributes_buffer.keys():
            raise StxError(f'The attribute {see(key)} was already defined.')

        self.attributes_buffer.put(key, value)

    def get_last_component(self) -> Optional[Component]:
        comps = self.components

        if len(comps) == 0:
            return None

        return comps[-1]

    def push_pre_caption(self, caption: Component):
        self.pre_captions.append(caption)

    def push_post_caption(self, caption: Component):
        consumed = False

        for comps in reversed(self.stack):
            if len(comps) > 0:
                component = comps[-1]

                if isinstance(component, Table):
                    component.caption = caption
                else:
                    figure = Figure(component.location, component, caption)

                    comps[-1] = figure

                consumed = True
                break

        if not consumed:
            raise StxError('Expected component for post-caption.')
