import sys

from stx.__main__ import main
from stx.parsing3.parser import parse_document
from stx.parsing3.source import Source
from stx.rendering.json.renderer import render_to_output, render_to_file
from stx.rendering.json.serializer import document_to_json

if __name__ == '__main__':
    # main(
    #     input_file='/Users/sergio/bm/docs/src/index.stx',
    #     output_file='/Users/sergio/bm/docs/docs/index.html'
    # )
    with Source.from_file('/Users/sergio/bm/docs/src/index.stx') as source:
        doc = parse_document(source)

    render_to_file(doc, '/Users/sergio/bm/docs/docs/index.json')

