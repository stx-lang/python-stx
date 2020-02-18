from typing import Optional, List

from stx.components import Component
from stx.outputs.output_task import OutputTask


class Document:

    def __init__(self, source_file):
        self.source_file = source_file
        self.title: Optional[str] = None
        self.author: Optional[str] = None
        self.format: Optional[str] = None
        self.encoding: Optional[str] = None
        self.header: Optional[Component] = None
        self.content: Optional[Component] = None
        self.footer: Optional[Component] = None
        self.stylesheets: List[str] = []
        self.outputs: List[OutputTask] = []
