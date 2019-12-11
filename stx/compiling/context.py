from os import path
from typing import Dict

from stx.components.content import CContent
from stx.reader import Reader

IDsMap = Dict[str, CContent]


class Context:

    def __init__(self):
        self.base_path = None
        self.encoding = None
        self.ids: IDsMap = {}
        self.linked_stylesheets = []

    def resolve_reader(self, file_path: str) -> Reader:
        return Reader.from_file(
            path.join(self.base_path, file_path), self.encoding)
