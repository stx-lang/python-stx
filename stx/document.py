from __future__ import annotations

from io import TextIOWrapper
from typing import Optional, List

from stx.action import Action
from stx.components import Component

import sys
from typing import Optional, TextIO

from stx import logger
from stx.compiling.reading.location import Location
from stx.data_notation.values import Value, Empty
from stx.utils.files import resolve_sibling
from stx.utils.stx_error import StxError
from stx.utils.debug import see


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
