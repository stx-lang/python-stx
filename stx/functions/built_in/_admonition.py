from typing import Optional

from stx.functions import utils
from stx.components import FunctionCall, Component, ContentBox
from stx.document import Document
from stx.utils.stx_error import StxError


def resolve_admonition(document: Document, call: FunctionCall) -> Component:
    options = utils.make_options_dict(call, key_for_str='type')

    data_type = options.pop('type', None)

    utils.check_unknown_options(options, call)

    return make_admonition(document, call, data_type)


def resolve_warning(document: Document, call: FunctionCall) -> Component:
    utils.check_unknown_options(call.options, call)

    return make_admonition(document, call, 'warning')


def resolve_information(document: Document, call: FunctionCall) -> Component:
    utils.check_unknown_options(call.options, call)

    return make_admonition(document, call, 'information')


def make_admonition(
        document: Document,
        call: FunctionCall,
        data_type: Optional[str]) -> Component:
    if call.argument is None:
        raise call.error('Admonitions require a captured component.')

    box = ContentBox(call.location)
    box.content = call.argument
    box.style = data_type

    return box
