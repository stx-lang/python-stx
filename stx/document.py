from typing import Optional

from stx.components import Component


class Document:

    def __init__(self):
        self.title = None
        self.author = None
        self.header = None
        self.content: Optional[Component] = None
        self.footer = None
        self.format = None
        self.encoding = None
        self.refs = None
        self.index = None
