from stx.compiling.resolvers import utils
from stx.components import FunctionCall, Component, Literal, CodeBlock
from stx.document import Document


def resolve_code(document: Document, call: FunctionCall) -> Component:
    text = utils.make_literal_arg(call)

    options = utils.make_options_dict(call, key_for_str='lang')

    lang = options.pop('lang', None)

    utils.check_unknown_options(options, call)

    return CodeBlock(call.location, text, lang=lang)
