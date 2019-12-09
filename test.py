from stx.compiling.compiler import from_file
from stx.html5.renderer import render_document
from stx.writting import HtmlWriter


if __name__ == '__main__':
    document = from_file('example/book.txt')

    with open("example/book.html", "w", encoding="utf-8") as f:
        html = render_document(HtmlWriter(f), document)
