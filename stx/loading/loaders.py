from stx.design.document import Document
from stx.loading.linking import link_component
from stx.loading.numbering import build_numbering
from stx.parsing import parse_from_file


def from_file(file_path: str) -> Document:
    doc = Document()

    doc.content = parse_from_file(doc, file_path)

    doc.refs = link_component(doc.content)

    doc.index = build_numbering(doc.content)

    return doc
