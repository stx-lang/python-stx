from os import path
from typing import Dict

from stx.components.content import CContent
from stx.reader import Reader

IDsMap = Dict[str, CContent]


class Context:

    def __init__(self, base_path: str, encoding: str):
        self.base_path = base_path
        self.encoding = encoding
        self.ids: IDsMap = {}

    def resolve_reader(self, file_path: str) -> Reader:
        return Reader.from_file(
            path.join(self.base_path, file_path), self.encoding)
