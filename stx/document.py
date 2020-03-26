from __future__ import annotations

from typing import List
from typing import Optional

from stx.action import Action
from stx.components import Component


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
        self.actions: List[Action] = []
