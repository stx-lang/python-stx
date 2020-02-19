from __future__ import annotations

from typing import List, Dict, Any


class Value:

    def as_token(self) -> Token:
        raise NotImplementedError()

    def as_entry(self) -> Entry:
        raise NotImplementedError()

    def as_group(self) -> Group:
        raise NotImplementedError()

    def to_any(self) -> Any:
        raise NotImplementedError()

    def to_str(self) -> str:
        raise NotImplementedError()

    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError()

    def to_list(self) -> List[Any]:
        raise NotImplementedError()

    def collapse(self) -> Value:
        raise NotImplementedError()


class Empty(Value):

    def as_token(self) -> Token:
        return Token('')

    def as_entry(self) -> Entry:
        return Entry('', self)

    def as_group(self) -> Group:
        return Group([])

    def to_any(self) -> Any:
        return None

    def to_str(self) -> str:
        return ''

    def to_dict(self) -> Dict[str, Any]:
        return {}

    def to_list(self) -> List[Any]:
        return []

    def collapse(self) -> Value:
        return self


class Token(Value):

    def __init__(self, text: str):
        self.text = text

    def as_token(self) -> Token:
        return self

    def as_entry(self) -> Entry:
        return Entry(self.text, Empty())

    def as_group(self) -> Group:
        return Group([self])

    def to_any(self) -> str:
        return self.text

    def to_str(self) -> str:
        return self.text

    def to_dict(self) -> Dict[str, Any]:
        return {self.text: None}

    def to_list(self) -> List[Any]:
        return [self.text]

    def collapse(self) -> Value:
        return self


class Entry(Value):

    def __init__(self, name: str, value: Value):
        self.name = name
        self.value = value

    def as_token(self) -> Token:
        if isinstance(self.value, Empty):
            raise Exception('Cannot convert to token.')
        return Token(self.name)

    def as_entry(self) -> Entry:
        return self

    def as_group(self) -> Group:
        return Group([self])

    def to_any(self) -> Any:
        return self.to_dict()

    def to_str(self) -> str:
        if not isinstance(self.value, Empty):
            raise Exception('Cannot convert to token.')
        return self.name

    def to_dict(self) -> Dict[str, Any]:
        return {self.name: self.value.to_any()}

    def to_list(self) -> List[Any]:
        return [self.to_any()]

    def collapse(self) -> Value:
        if isinstance(self.value, Empty):
            return Token(self.name)
        return self


class Group(Value):

    def __init__(self, items: List[Value]):
        self.items = items

    def as_token(self) -> Token:
        length = len(self.items)

        if length == 1:
            return self.items[0].as_token()

        raise Exception('Cannot convert to token.')

    def as_entry(self) -> Entry:
        length = len(self.items)

        if length == 1:
            return Entry(self.items[0].to_str(), Empty())
        elif length == 2:
            return Entry(self.items[0].to_str(), self.items[1])

        raise Exception('Cannot convert to entry')

    def as_group(self) -> Group:
        return self

    def to_any(self) -> Any:
        entries = 0
        other = 0

        for item in self.items:
            if isinstance(item, Entry):
                entries += 1
            else:
                other += 1

        if entries > 0 and other == 0:
            return self.to_dict()
        return self.to_list()

    def to_str(self) -> str:
        length = len(self.items)

        if length == 0:
            return ''
        elif length == 1:
            return self.items[0].to_str()

        raise Exception('Cannot convert to str.')

    def to_dict(self) -> Dict[str, Any]:
        d = {}

        for item in self.items:
            entry = item.as_entry()

            if entry.name in d:
                raise Exception('already defined')

            d[entry.name] = entry.value.to_any()

        return d

    def to_list(self) -> List[Any]:
        return [item.to_any() for item in self.items]

    def collapse(self) -> Value:
        length = len(self.items)

        if length == 0:
            return Empty()
        elif length == 1:
            return self.items[0].collapse()

        return self
