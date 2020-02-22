from stx.compiling.linking.numbering import link_document_numbers
from stx.compiling.linking.referencing import link_document_references
from stx.compiling.linking.toc import link_document_tocs
from stx.compiling.parsing.parser import capture, CTX
from stx.compiling.resolvers.core import resolve_document
from stx.compiling.reading.reader import Reader
from stx.document import Document
from stx.utils.thread_context import context


def compile_document(file_path: str) -> Document:
    doc = Document(file_path)
    reader = Reader()
    ctx = CTX(doc, reader)

    context.push_reader(reader)

    reader.push_file(file_path)

    capture(ctx)

    context.pop_reader()

    link_document_references(doc)
    link_document_numbers(doc)
    link_document_tocs(doc)

    resolve_document(doc)

    # TODO validate links here

    return doc
