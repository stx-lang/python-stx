from typing import List, Any


def to_str(value: Any) -> str:
    if isinstance(value, str):
        return value
    elif value is None:
        return ''
    return str(value)


def to_list(value: Any) -> list:
    if isinstance(value, list):
        return value
    elif value is None:
        return []
    return [value]


def to_list_str(value: Any) -> List[str]:
    return [to_str(item) for item in to_list(value)]
