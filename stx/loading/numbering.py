from __future__ import annotations

from typing import List

from stx import logger
from stx.design.index_node import IndexNode
from stx.utils.stack import Stack
from stx.components import Figure, Table, Heading, Component


def build_numbering(document: Component) -> List[IndexNode]:
    logger.info('Building numbering...')

    index: List[IndexNode] = []
    stack: Stack[IndexNode] = Stack()
    figures: List[Figure] = []
    tables: List[Table] = []

    for content in document.walk():
        if isinstance(content, Heading):
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
        elif isinstance(content, Table):
            tables.append(content)
        elif isinstance(content, Figure):
            figures.append(content)

    logger.info('Applying numbering...')
    apply_heading_numbers('', index, 3)
    apply_table_numbers(tables)
    apply_figure_numbers(figures)

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


def apply_table_numbers(tables: List[Table]):
    count = 1

    for table in tables:
        table.number = f'Table {count}.'
        count += 1


def apply_figure_numbers(figures: List[Figure]):
    count = 1

    for figure in figures:
        figure.number = f'Figure {count}.'
        count += 1
