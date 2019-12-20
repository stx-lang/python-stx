from stx.html5.renderer import render_document
from stx.loaders import from_file
from stx.writting import HtmlWriter


def main():
    file_path = '/Users/sergio/bm/docs/src/index.stx'

    document = from_file(file_path)

    with open("/Users/sergio/bm/docs/docs/index.html", "w", encoding="utf-8") as f:
        render_document(document, HtmlWriter(f))

    print(document)


if __name__ == '__main__':
    main()
