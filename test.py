from stx.compiling.compiler import from_file
from stx.compiling.context import Context
from stx.html5.renderer import render_document
from stx.writting import HtmlWriter


if __name__ == '__main__':
    context = Context()
    document = from_file(context, '/Users/sergio/bm/docs/src/index.stx')

    with open("/Users/sergio/bm/docs/docs/index.html", "w", encoding="utf-8") as f:
        html = render_document(context, HtmlWriter(f), document)
