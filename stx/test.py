import sys

from stx.__main__ import main
from stx.design.document import Document
from stx.parsing3.parsers import Parser
from stx.parsing3.source import Source
from stx.rendering.json.renderer import render_to_output, render_to_file
from stx.rendering.json.serializer import document_to_json

if __name__ == '__main__':
    # with Source.from_file('/Users/sergio/bakasoft/stx/docs/index.stx') as source:
    #     doc = consume_document(source)
    #
    # render_to_file(doc, '/Users/sergio/bakasoft/stx/docs/index.json')

    # with Source.from_file('/Users/sergio/bm/docs/src/index.stx') as source:
    #     doc = consume_document(source)
    #
    # render_to_file(doc, '/Users/sergio/bm/docs/docs/index.json')

    doc = Document()
    parser = Parser(doc)

    with Source.from_file('/Users/sergio/bakasoft/stx/docs/test.stx') as source:
        parser.capture(source)

    render_to_file(doc, '/Users/sergio/bakasoft/stx/docs/test.json')
