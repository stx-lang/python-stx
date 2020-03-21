from stx.compiling.linking.numbering import link_document_numbers
from stx.compiling.linking.referencing import validate_references
from stx.compiling.linking.referencing import auto_generate_special_references
from stx.compiling.parsing.parser import capture, CTX
from stx.functions.core import resolve_document
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

    auto_generate_special_references(doc)

    link_document_numbers(doc)

    resolve_document(doc)

    validate_references(doc)

    return doc
