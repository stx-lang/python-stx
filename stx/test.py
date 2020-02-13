import os
import sys

from stx.compiling.compiler import compile_document
from stx.rendering.html5.serializer import document_to_html
from stx.rendering.json.renderer import render_to_file

if __name__ == '__main__':
    # stx_file = '/Users/sergio/bakasoft/stx/docs/test.stx'
    # out_file = '/Users/sergio/bakasoft/stx/docs/test.json'

    # stx_file = '/Users/sergio/bakasoft/stx/docs/index.stx'
    # out_file = '/Users/sergio/bakasoft/stx/docs/index.json'

    stx_file = '/Users/sergio/bm/docs/src/index.stx'
    json_file = '/Users/sergio/bm/docs/docs/index.json'
    html_file = '/Users/sergio/bm/docs/docs/index.html'

    try:
        os.remove(json_file)
    except:
        pass

    doc = compile_document(stx_file)

    render_to_file(doc, json_file)

    html = document_to_html(doc)

    with open(html_file, 'w') as output:
        for tag in html:
            tag.render(output)
