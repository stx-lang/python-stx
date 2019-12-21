from stx.rendering.html5.renderer import render_document
from stx.loading.loaders import from_file
from stx.rendering.html5.writer import HtmlWriter


def main():
    file_path = './docs/index.stx'

    document = from_file(file_path)

    with open('./docs/index.html', 'w', encoding='utf-8') as f:
        render_document(document, HtmlWriter(f))


if __name__ == '__main__':
    main()
