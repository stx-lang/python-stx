from __future__ import annotations

from io import StringIO
from typing import List, Iterable, TextIO, Union, Optional

from stx.compiling.reading.location import Location
from stx.utils.stx_error import StxError
from stx.utils.debug import see


class Component:
    ref: Union[str, List[str], None] = None
    location: Optional[Location] = None

    def get_refs(self) -> List[str]:
        if self.ref is None:
            return []
        elif isinstance(self.ref, list):
            return [str(r) for r in self.ref]
        return [str(self.ref)]

    def get_main_ref(self) -> Optional[str]:
        refs = self.get_refs()

        if len(refs) == 0:
            return None

        return refs[0]

    def add_ref(self, ref):
        refs = self.get_refs()
        if ref not in refs:
            refs.append(ref)
        self.ref = refs

    def has_refs(self) -> bool:
        if isinstance(self.ref, list):
            return len(self.ref) > 0
        return self.ref is not None

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
