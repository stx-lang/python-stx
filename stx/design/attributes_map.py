from __future__ import annotations

from typing import Dict, Optional, List, Set


class AttributesMap:

    def __init__(self):
        self._data: Dict[str, List[str]] = {}
        self._read: Dict[str, bool] = {}

    def __len__(self):
        return len(self._data)

    def get_unread_attributes(self) -> Set[str]:
        total_keys = set(self._data.keys())
        read_keys = set([key for key, read in self._read.items() if read])
        return total_keys - read_keys

    def update(self, other_map: AttributesMap):
        self._data = dict(other_map._data)
        self._read.clear()

    def clear(self):
        self._data.clear()
        self._read.clear()

    def add_values(self, name: str, values: List[str]):
        if self._data.get(name, None) is None:
            self._data[name] = []

        self._data[name].extend(values)

    def get_value(
            self,
            name: str,
            default: Optional[str] = None) -> Optional[str]:
        values = self._data.get(name, None)

        self._read[name] = True

        if values is None or len(values) == 0:
            return default
        elif len(values) > 1:
            raise Exception(f'Too much values: {name}')

        return values[0]

    def get_list(self, name: str) -> List[str]:
        values = self._data.get(name, None)

        self._read[name] = True

        if values is None:
            return []

        return values
