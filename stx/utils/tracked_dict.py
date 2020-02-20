from typing import Generic, TypeVar, Optional, Dict, Set, List

KT = TypeVar('KT')
VT = TypeVar('VT')


class TrackedDict(Generic[KT, VT]):

    def __init__(self, source: Dict[KT, VT]):
        self._source = source
        self._active_keys: Set[KT] = set()

    def get(self, key: KT) -> Optional[VT]:
        self._active_keys.add(key)
        return self._source.get(key, None)

    def put(self, key: KT, value: VT):
        self._source[key] = value

    def clear(self):
        self._source.clear()

    def empty(self) -> bool:
        return len(self._source) == 0

    def unknown_keys(self) -> Set[KT]:
        return self._source.keys() - self._active_keys

    def active_keys(self) -> Set[KT]:
        return set(self._active_keys)

    def missing_keys(self) -> Set[KT]:
        return self._active_keys - self._source.keys()

    def keys(self):
        return self._source.keys()
