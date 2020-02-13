import os

from stx.compiling.compiler import compile_document
from stx.rendering.json.renderer import render_to_file

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

    doc = compile_document(stx_file)

    render_to_file(doc, out_file)
