from stx.compiling.compiler import compile_block
from stx.compiling.validator import build_links
from stx.html5.renderer import render_document
from stx.parsing.block import parse
from stx.reader import Reader
from stx.utils import Stack
from stx.writting import HtmlWriter


def main():
    pass


class Abc:

    def __init__(self, x):
        self.x = x


if __name__ == '__main__':
    with open("example/book.txt", "r", encoding="utf-8") as f:
        content = f.read()

    reader = Reader(content)

    block = parse(reader, Stack())

    document = compile_block(block)

    build_links(document)

    with open("example/book.html", "w", encoding="utf-8") as f:
        html = render_document(HtmlWriter(f), document)
