import click

from stx.loading.loaders import from_file
from stx.rendering.html5.renderer import render_document
from stx.rendering.html5.writer import HtmlWriter


@click.command()
@click.argument('input_file')
@click.argument('output_file')
@click.option('--output_format', default='html5')
@click.option('--output_encoding', default='utf-8')
def main(
        input_file: str,
        output_file: str,
        output_format: str,
        output_encoding: str):
    document = from_file(input_file)

    if output_format == 'html5':
        with open(output_file, 'w', encoding=output_encoding) as f:
            render_document(document, HtmlWriter(f))
    else:
        raise Exception(f'Not implemented output format: {output_format}')


if __name__ == '__main__':
    main()
