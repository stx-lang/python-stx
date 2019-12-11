from __future__ import annotations

from typing import List

from stx.components.content import CHeading


class IndexNode:

    def __init__(self, heading: CHeading):
        self.heading = heading
        self.level = heading.level
        self.nodes: List[IndexNode] = []

    def add(self, node: IndexNode):
        self.nodes.append(node)
