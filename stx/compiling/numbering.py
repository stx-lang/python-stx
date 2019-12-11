from __future__ import annotations

from typing import List, Dict, Optional

from stx.compiling.context import Context
from stx.components.content import CContent, CContainer, CHeading, CTable
from stx.utils import Stack


class IndexNode:

    def __init__(self, heading: CHeading):
        self.heading = heading
        self.level = heading.level
        self.nodes: List[IndexNode] = []

    def add(self, node: IndexNode):
        self.nodes.append(node)


def build_numbering(context: Context, document: CContent):
    index: List[IndexNode] = []
    stack: Stack[IndexNode] = Stack()
    tables: List[CTable] = []
    figures = []

    for content in document.walk():
        if isinstance(content, CHeading):
            node = IndexNode(content)
            level = content.level

            if stack.empty():
                index.append(node)
                stack.push(node)
            elif level > stack.peek().level:
                stack.peek().add(node)
                stack.push(node)
            elif level == stack.peek().level:
                if stack.empty():
                    raise Exception('Invalid state')
                stack.pop()
                if stack.empty():
                    index.append(node)
                else:
                    stack.peek().add(node)
                stack.push(node)
            else:
                while not stack.empty() and level <= stack.peek().level:
                    stack.pop()

                if stack.empty():
                    index.append(node)
                else:
                    stack.peek().add(node)

                stack.push(node)
        elif isinstance(content, CTable):
            if content.caption is not None:
                tables.append(content)

    apply_heading_numbers('', index, 3)
    apply_table_numbers(tables)

    return index


def apply_heading_numbers(
        parent: str, nodes: List[IndexNode], max_levels: int, level: int = 1):
    count = 1
    for node in nodes:
        number = f'{count}.'

        if parent:
            number = f'{parent}{number}'

        node.heading.number = number

        count += 1

        if level < max_levels:
            apply_heading_numbers(number, node.nodes, max_levels, level + 1)


def apply_table_numbers(tables: List[CTable]):
    count = 1

    for table in tables:
        table.number = f'Table {count}.'

        count += 1
