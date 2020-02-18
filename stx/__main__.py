import click

from stx.app import main


@click.command()
@click.argument('input_file')
def cli(input_file: str):
    main(input_file)


if __name__ == '__main__':
    cli()
