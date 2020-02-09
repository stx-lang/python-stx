from typing import List

from stx.components import Placeholder
from stx.design.document import Document
from stx.parsing._composer import Composer
from stx.parsing._source import Source


def process_link(document: Document, values: list):
    if len(values) < 2:
        raise Exception('Expected rel and files')

    rel = values[0]

    document.links.add_values(rel, values[1:])


def process_title(document: Document, values: list):
    if len(values) != 1:
        raise Exception('Expected title')

    document.title = values[0]


def process_author(document: Document, values: list):
    if len(values) != 1:
        raise Exception('Expected author')

    document.author = values[0]


def process_format(document: Document, values: list):
    if len(values) != 1:
        raise Exception('Expected format')

    document.format = values[0]


def process_encoding(document: Document, values: list):
    if len(values) != 1:
        raise Exception('Expected encoding')

    document.encoding = values[0]


def process_toc(document: Document, values: list, composer: Composer):
    composer.push(Placeholder('toc'))


def process_directive(name: str, values: List[str], document: Document, source: Source, composer: Composer):
    if name == 'link':
        process_link(document, values)
    elif name == 'format':
        process_format(document, values)
    elif name == 'encoding':
        process_encoding(document, values)
    elif name == 'title':
        process_title(document, values)
    elif name == 'author':
        process_author(document, values)
    elif name == 'toc':
        process_toc(document, values, composer)
    else:
        raise Exception(f'Not implemented directive: {name}')
