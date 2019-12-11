from __future__ import annotations

from typing import List, Dict, Optional

from stx.compiling.context import Context
from stx.compiling.index_node import IndexNode
from stx.components.content import CContent, CContainer, CHeading, CTable, \
    CFigure
from stx.utils import Stack


def build_numbering(context: Context, document: CContent):
    index: List[IndexNode] = []
    stack: Stack[IndexNode] = Stack()
    figures: List[CFigure] = []
    tables: List[CTable] = []

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
            tables.append(content)
        elif isinstance(content, CFigure):
            figures.append(content)

    apply_heading_numbers('', index, 3)
    apply_table_numbers(tables)
    apply_figure_numbers(figures)

    context.index = index

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


def apply_figure_numbers(figures: List[CFigure]):
    count = 1

    for figure in figures:
        figure.number = f'Figure {count}.'
        count += 1
