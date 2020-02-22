from stx.compiling.resolvers import utils
from stx.components import FunctionCall, Component, Literal
from stx.document import Document


def resolve_code(document: Document, call: FunctionCall) -> Component:
    text = utils.make_literal_arg(call)

    options_dict = utils.make_options_dict(call, key_for_str='lang')

    lang = options_dict.pop('lang', None)

    utils.options_dict_must_be_empty(options_dict, call)

    return Literal(call.location, text, lang=lang)
