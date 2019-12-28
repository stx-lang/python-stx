import click

from stx.app import main


@click.command()
@click.argument('input_file')
@click.argument('output_file')
def cli(
        input_file: str,
        output_file: str):
    main(
        input_file=input_file,
        output_file=output_file,
    )


if __name__ == '__main__':
    cli()
