from __future__ import annotations

from typing import List

from stx.design.components import Heading


class IndexNode:

    def __init__(self, heading: Heading):
        self.heading = heading
        self.level = heading.level
        self.nodes: List[IndexNode] = []

    def add(self, node: IndexNode):
        self.nodes.append(node)
