from stx.compiling.compiler import from_file
from stx.compiling.context import Context
from stx.compiling.numbering import build_numbering
from stx.compiling.validator import build_links
from stx.html5.renderer import render_document
from stx.writting import HtmlWriter


if __name__ == '__main__':
    context = Context()
    document = from_file(context, '/Users/sergio/bm/docs/src/index.stx')

    build_links(context, document)
    build_numbering(context, document)

    with open("/Users/sergio/bm/docs/docs/index.html", "w", encoding="utf-8") as f:
        render_document(context, HtmlWriter(f), document)
