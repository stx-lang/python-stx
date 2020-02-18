from stx import logger
from stx.compiling.compiler import compile_document
from stx.outputs import registry
from stx.utils.files import resolve_sibling


def read_version() -> str:
    version_file = resolve_sibling(__file__, '../version.txt')

    with open(version_file, 'r') as f:
        return f.read().strip()


version = read_version()
name = 'STX'
title = f'{name} {version}'


def main(input_file: str):
    document = compile_document(input_file)

    for output in document.outputs:
        logger.info(f'Generating {output.format} output...')

        renderer = registry.get_renderer(output.format)

        renderer(document, output)
