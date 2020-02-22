from stx.compiling.resolvers import utils
from stx.components import Component, FunctionCall, PlainText, CustomText
from stx.document import Document


def resolve_custom_style(document: Document, call: FunctionCall) -> Component:
    options = utils.make_options_dict(call, key_for_str='style')
    contents = utils.make_component_list_arg(call)

    custom_style = options.pop('style')

    utils.check_unknown_options(options, call)

    return CustomText(call.location, contents, custom_style)
