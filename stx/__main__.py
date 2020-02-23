import click

from stx.app import main


@click.command()
@click.argument('input_file')
@click.option('--watch', is_flag=True, default=False)
def cli(input_file: str, watch: bool):
    main(input_file, watch)


if __name__ == '__main__':
    cli()
