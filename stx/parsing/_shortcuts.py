from stx.components import Component
from stx.design.document import Document

from ._parsing import parse_component
from ._source import Source


def parse_from_file(document: Document, file_path: str) -> Component:
    with open(file_path, 'r') as stream:
        source = Source(stream, file_path)

        return parse_component(document, source)