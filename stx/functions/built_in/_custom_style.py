from stx.functions import utils
from stx.components import Component, FunctionCall, CustomText
from stx.document import Document


def resolve_custom_style(document: Document, call: FunctionCall) -> Component:
    if call.argument is None:
        raise call.error(
            'Custom style function requires a captured component.')

    options = utils.make_options_dict(call, key_for_str='style')
    contents = utils.make_component_list(call.argument)

    custom_style = options.pop('style')

    utils.check_unknown_options(options, call)

    return CustomText(call.location, contents, custom_style)
