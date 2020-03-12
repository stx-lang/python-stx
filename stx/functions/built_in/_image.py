from stx import logger
from stx.functions import utils
from stx.components import Component, Image, FunctionCall
from stx.document import Document
from stx.utils.stx_error import StxError


def resolve_image(document: Document, call: FunctionCall) -> Component:
    options = utils.make_options_dict(call, 'src')

    src = options.pop('src', None)
    alt = options.pop('alt', None)

    utils.check_unknown_options(options, call)

    if src is None:
        raise StxError(f'Missing `src` parameter in image.', call.location)
    elif not alt:
        logger.warning('Image without `alt`', call.location)

    return Image(call.location, src, alt)
