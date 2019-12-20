from os import path, walk
from typing import Iterator

from stx import marks


def resolve_path(base_path: str, relative_path: str) -> str:
    if path.isabs(relative_path):
        return relative_path

    return path.normpath(path.join(base_path, relative_path))


def resolve_sibling(main_path: str, relative_path: str) -> str:
    base_dir = path.dirname(main_path)

    return resolve_path(base_dir, relative_path)


def walk_files(dir_path: str) -> Iterator[str]:
    for root, dirs, files in walk(dir_path):
        for name in files:
            yield path.join(root, name)


def is_escaped(text: str, index: int) -> bool:
    return 0 < index < len(text) and text[index - 1] == marks.escape_mark


def find_str(source: str, target: str) -> int:
    if target is None:
        return -1
    try:
        return source.index(target)
    except ValueError:
        return -1


def crop_text(text: str, length: int, append_ellipsis=True) -> str:
    if len(text) <= length:
        return text

    return text[:length] + '...'
