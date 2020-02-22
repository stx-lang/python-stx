from __future__ import annotations

from io import StringIO
from typing import List, Iterable, TextIO, Union, Optional, Dict

from stx.compiling.reading.location import Location
from stx.data_notation.values import Value, Token
from stx.utils.stx_error import StxError
from stx.utils.debug import see
from stx.utils.tracked_dict import TrackedDict


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

    def get_other_refs(self) -> List[str]:
        refs = self.get_refs()

        if len(refs) > 0:
            refs.pop(0)

        return refs

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

    def apply_attributes(self, attributes: TrackedDict[str, Value]):
        ref_value = attributes.get('ref')

        if ref_value is not None:
            ref_token = ref_value.try_token()

            if ref_token is not None:
                self.ref = ref_token.to_str()
            else:
                self.ref = ref_value.to_list()

        self.apply_advanced_attributes(attributes)

    def apply_advanced_attributes(self, attributes: TrackedDict[str, Value]):
        raise NotImplementedError()
