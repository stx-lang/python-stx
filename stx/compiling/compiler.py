from stx.compiling.linking.numbering import link_document_numbers
from stx.compiling.linking.referencing import link_document_references
from stx.compiling.linking.toc import link_document_tocs
from stx.compiling.parsing.parser import Parser
from stx.compiling.processing.core import process_document_macros
from stx.document import Document
from stx.utils.thread_context import context


def compile_document(file_path: str) -> Document:
    doc = Document(file_path)

    parser = Parser(doc)

    context.push_parser(parser)

    parser.push_file(file_path)
    parser.capture()

    context.pop_parser()

    link_document_references(doc)
    link_document_numbers(doc)
    link_document_tocs(doc)

    process_document_macros(doc)

    return doc
