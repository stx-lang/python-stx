from stx import logger
from stx.compiling.reading.location import Location
from stx.components import Component, Image
from stx.data_notation.values import Value, Token
from stx.document import Document
from stx.utils.stx_error import StxError


def process_image(
        document: Document, location: Location, value: Value) -> Component:
    value = value.collapse()

    if isinstance(value, Token):
        src = value.to_str()
        alt = None
    else:
        d = value.to_dict()
        src = d.get('src', None)
        alt = d.get('alt', None)

    if src is None:
        raise StxError(f'Missing `src` parameter in image.', location)
    elif not alt:
        logger.warning('Image without `alt`', location)

    return Image(location, src, alt)