from stx import logger
from stx.functions import utils
from stx.components import Component, FunctionCall, Literal
from stx.document import Document
from stx.utils.files import resolve_sibling
from stx.utils.stx_error import StxError


def resolve_embed(document: Document, call: FunctionCall) -> Component:
    options = utils.make_options_dict(call, 'src')

    src = options.pop('src', None)

    utils.check_unknown_options(options, call)

    if src is None:
        raise StxError(f'Missing `src` parameter in embed.', call.location)

    src = resolve_sibling(document.source_file, src)

    logger.info(f'Embedding: {src}')

    with open(src, 'r', encoding='UTF-8') as f:
        text = f.read()

    # TODO add support for more type of files

    return Literal(call.location, text, source=src)
