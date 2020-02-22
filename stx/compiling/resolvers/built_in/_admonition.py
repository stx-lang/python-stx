from typing import Optional

from stx.compiling.resolvers import utils
from stx.components import FunctionCall, Component, Literal
from stx.data_notation.values import Value
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


def make_admonition(
        document: Document,
        call: FunctionCall,
        data_type: Optional[str]) -> Component:
    content = utils.make_component_arg(call)

    # TODO implement wrapper component with meta-data
    return content
