from os import path
from typing import Dict, List, Optional

from stx import logger
from stx.compiling.index_node import IndexNode
from stx.components.content import CContent
from stx.link_map import RefMap
from stx.reader import Reader

IDsMap = Dict[str, CContent]


class Context:

    def __init__(self):
        self.base_path = None
        self.encoding = None
        self.links = RefMap()
        self.linked_stylesheets = []
        self.index: Optional[List[IndexNode]] = None

    def resolve_reader(self, file_path: str) -> Reader:
        logger.info(f'Resolving file {file_path}...')
        return Reader.from_file(
            path.join(self.base_path, file_path), self.encoding)
