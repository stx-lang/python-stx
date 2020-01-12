from stx.loading.loaders import from_file
from stx.rendering.html5.renderer import render_document
from stx.rendering.html5.writer import HtmlWriter
from stx.utils.files import resolve_sibling
from stx.loading.validations import validate_attributes


def read_version() -> str:
    version_file = resolve_sibling(__file__, '../version.txt')

    with open(version_file, 'r') as f:
        return f.read().strip()


version = read_version()
name = 'STX'
title = f'{name} {version}'


def main(input_file, output_file):
    document = from_file(input_file)

    if document.format is None:
        document.format = 'html5'

    if document.encoding is None:
        document.encoding = 'UTF-8'

    if document.format == 'html5':
        with open(output_file, 'w', encoding=document.encoding) as f:
            render_document(document, HtmlWriter(f))
    else:
        raise Exception(f'Not implemented output format: {document.format}')

    validate_attributes(document)