from __future__ import annotations

from typing import List, Dict, Any, Optional


class Value:

    def to_any(self) -> Any:
        raise NotImplementedError()

    def to_map(self) -> Dict[str, Value]:
        raise NotImplementedError()

    def try_token(self) -> Optional[Token]:
        raise NotImplementedError()

    def try_entry(self) -> Optional[Entry]:
        raise NotImplementedError()

    def try_group(self) -> Optional[Group]:
        raise NotImplementedError()

    def try_str(self) -> Optional[str]:
        raise NotImplementedError()

    def try_dict(self) -> Optional[Dict[str, Any]]:
        raise NotImplementedError()

    def try_list(self) -> Optional[List[Any]]:
        raise NotImplementedError()

    def to_token(self) -> Token:
        token = self.try_token()

        if token is None:
            raise Exception('Cannot convert to token.')

        return token

    def to_entry(self) -> Entry:
        entry = self.try_entry()

        if entry is None:
            raise Exception('Cannot convert to entry.')

        return entry

    def to_group(self) -> Group:
        group = self.try_group()

        if group is None:
            raise Exception('Cannot convert to group.')

        return group

    def to_str(self) -> str:
        s = self.try_str()

        if s is None:
            raise Exception('Cannot convert to str.')

        return s

    def to_dict(self) -> Dict[str, Any]:
        d = self.try_dict()

        if d is None:
            raise Exception('Cannot convert to dict.')

        return d

    def to_list(self) -> List[Any]:
        lst = self.try_list()

        if lst is None:
            raise Exception('Cannot convert to list.')

        return lst


class Empty(Value):

    def to_any(self) -> Any:
        return None

    def to_map(self) -> Dict[str, Value]:
        return {}

    def try_token(self) -> Optional[Token]:
        return None

    def try_entry(self) -> Optional[Entry]:
        return None

    def try_group(self) -> Optional[Group]:
        return None

    def try_str(self) -> Optional[str]:
        return None

    def try_dict(self) -> Optional[Dict[str, Any]]:
        return None

    def try_list(self) -> Optional[List[Any]]:
        return None


class Token(Value):

    def __init__(self, text: str):
        self.text = text

    def to_token(self) -> Token:
        return self

    def to_str(self) -> str:
        return self.text

    def to_any(self) -> Any:
        return self.text

    def to_map(self) -> Dict[str, Value]:
        return {self.text: Empty()}

    def try_token(self) -> Optional[Token]:
        return self

    def try_entry(self) -> Optional[Entry]:
        return Entry(self.text, Empty())

    def try_group(self) -> Optional[Group]:
        return Group([self])

    def try_str(self) -> Optional[str]:
        return self.text

    def try_dict(self) -> Optional[Dict[str, Any]]:
        return {self.text: None}

    def try_list(self) -> Optional[List[Any]]:
        return [self.text]


class Entry(Value):

    def __init__(self, name: str, value: Value):
        self.name = name
        self.value = value

    def to_entry(self) -> Entry:
        return self

    def to_dict(self):
        return {self.name: self.value.to_any()}

    def to_any(self) -> Any:
        return self.to_dict()

    def to_map(self) -> Dict[str, Value]:
        return {self.name: self.value}

    def try_token(self) -> Optional[Token]:
        if isinstance(self.value, Empty):
            return Token(self.name)
        return None

    def try_entry(self) -> Optional[Entry]:
        return self

    def try_group(self) -> Optional[Group]:
        return Group([self])

    def try_str(self) -> Optional[str]:
        if isinstance(self.value, Empty):
            return self.name
        return None

    def try_dict(self) -> Optional[Dict[str, Any]]:
        return self.to_dict()

    def try_list(self) -> Optional[List[Any]]:
        return [self.to_any()]


class Group(Value):

    def __init__(self, items: List[Value]):
        self.items = items

    def to_group(self) -> Group:
        return self

    def try_group(self) -> Optional[Group]:
        return self

    def to_list(self) -> List[Any]:
        return [item.to_any() for item in self.items]

    def try_list(self) -> Optional[List[Any]]:
        return self.to_list()

    def to_any(self) -> Any:
        entries = 0
        tokens = 0
        other = 0

        for item in self.items:
            if isinstance(item, Entry):
                entries += 1
            elif isinstance(item, Token):
                tokens += 1
            else:
                other += 1

        if entries > 0 and other == 0:
            d = self.try_dict()
            if d is not None:
                return d

        return self.to_list()

    def to_map(self) -> Dict[str, Value]:
        d = {}

        for item in self.items:
            entry = item.to_entry()

            d[entry.name] = entry.value

        return d

    def try_token(self) -> Optional[Token]:
        length = len(self.items)

        if length == 1:
            return self.items[0].try_token()

        return None

    def try_entry(self) -> Optional[Entry]:
        length = len(self.items)

        if length == 1:
            key = self.items[0].try_str()
            value = None
        elif length == 2:
            key = self.items[0].try_str()
            value = self.items[1]
        else:
            key = None
            value = None

        if key is not None:
            if value is None:
                value = Empty()
            return Entry(key, value)
        return None

    def try_str(self) -> Optional[str]:
        length = len(self.items)

        if length == 1:
            return self.items[0].try_str()

        return None

    def try_dict(self) -> Optional[Dict[str, Any]]:
        d = {}

        for item in self.items:
            entry = item.try_entry()

            if entry is None or entry.name in d:
                return None

            d[entry.name] = entry.value.to_any()

        return d
