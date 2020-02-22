from stx import logger
from stx.compiling.reading.location import Location
from stx.components import Component, Image, FunctionCall
from stx.data_notation.values import Value, Token
from stx.document import Document
from stx.utils.stx_error import StxError


def resolve_image(document: Document, call: FunctionCall) -> Component:
    value = call.options.collapse()

    if isinstance(value, Token):
        src = value.to_str()
        alt = None
    else:
        d = value.to_dict()
        src = d.get('src', None)
        alt = d.get('alt', None)

    if src is None:
        raise StxError(f'Missing `src` parameter in image.', call.location)
    elif not alt:
        logger.warning('Image without `alt`', call.location)

    return Image(call.location, src, alt)
