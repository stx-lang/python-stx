import os
import sys

from stx.__main__ import main
from stx.design.document import Document
from stx.compiling.parsing.parser import Parser
from stx.rendering.json.renderer import render_to_output, render_to_file
from stx.rendering.json.serializer import document_to_json

if __name__ == '__main__':
    # stx_file = '/Users/sergio/bakasoft/stx/docs/test.stx'
    # out_file = '/Users/sergio/bakasoft/stx/docs/test.json'

    # stx_file = '/Users/sergio/bakasoft/stx/docs/index.stx'
    # out_file = '/Users/sergio/bakasoft/stx/docs/index.json'

    stx_file = '/Users/sergio/bm/docs/src/index.stx'
    out_file = '/Users/sergio/bm/docs/docs/index.json'

    try:
        os.remove(out_file)
    except:
        pass

    doc = Document()

    parser = Parser(doc)
    parser.push_file(stx_file)
    parser.capture()

    render_to_file(doc, out_file)
