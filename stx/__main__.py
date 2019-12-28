import click

from stx.app import main


@click.command()
@click.argument('input_file')
@click.argument('output_file')
@click.option('--output_encoding', default='utf-8')
def cli(
        input_file: str,
        output_file: str,
        output_encoding: str):

    main(
        input_file=input_file,
        output_file=output_file,
        output_encoding=output_encoding,
    )


if __name__ == '__main__':
    cli()
