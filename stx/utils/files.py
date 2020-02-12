from os import path, walk
from typing import Iterator, List, Iterable


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


def resolve_include_files(include_path: str, source_path: str) -> List[str]:
    target_path = resolve_sibling(source_path, include_path)

    if path.isdir(target_path):
        return [file_path for file_path in sorted(walk_files(target_path))]

    return [target_path]
