from __future__ import annotations

from io import StringIO
from typing import List, Iterable, TextIO, Union

from stx.utils.stx_error import StxError
from stx.utils.debug import see


class Component:
    ref: Union[str, List[str], None] = None

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

    def apply_attributes(self, attributes: dict):
        for key, value in attributes.items():
            if not hasattr(self, key):
                raise StxError(
                    f'Component {see(self)} does not'
                    f' support the attribute {see(key)}.')

            setattr(self, key, value)
