from stx.compiling.resolvers import utils
from stx.components import Component, FunctionCall, PlainText
from stx.document import Document


def resolve_line_feed(document: Document, call: FunctionCall) -> Component:
    utils.check_unknown_options(call.options, call)

    return PlainText(call.location, '\n')
