from stx.functions import utils
from stx.components import FunctionCall, Component, Layout
from stx.document import Document


def layout_function(document: Document, call: FunctionCall) -> Component:
    if call.argument is None:
        raise call.error('Layouts require a captured component.')

    components = utils.make_component_list(call.argument)

    options = utils.make_options_dict(call, key_for_str='dir')

    direction = options.pop('dir', None)

    utils.check_unknown_options(options, call)

    return Layout(call.location, components, direction)
