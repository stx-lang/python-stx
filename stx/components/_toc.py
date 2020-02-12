from __future__ import annotations

import re
from io import StringIO
from typing import List, Iterable, Optional, TextIO

from ._component import Component


class TableOfContents(Component):

    def __init__(self):
        self.title: Optional[str] = None

    def write_text(self, output: TextIO):
        pass

    def get_children(self) -> List[Component]:
        return []
