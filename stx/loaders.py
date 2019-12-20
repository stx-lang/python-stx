from stx.document import Document
from stx.linking import link_component
from stx.numbering import build_numbering
from stx.parsing import parse_component
from stx.parsing_classes import Source


def from_file(file_path: str) -> Document:
    doc = Document()

    with open(file_path, 'r') as stream:
        source = Source(stream, file_path)

        doc.content = parse_component(doc, source)

        doc.refs = link_component(doc.content)

        doc.index = build_numbering(doc.content)

    return doc