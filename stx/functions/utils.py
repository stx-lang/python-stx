from io import StringIO
from typing import Optional, Union, List

from stx import logger
from stx.components import FunctionCall, Component, Literal, Composite, \
    Paragraph
from stx.data_notation.values import Value
from stx.utils.stx_error import StxError
from stx.utils.debug import see


def make_options_dict(call: FunctionCall, key_for_str: Optional[str] = None):
    options = call.options

    if key_for_str is not None:
        options_str = options.try_str()

        if options_str is not None:
            return {key_for_str: options_str}

    value = options.to_any()

    if value is None:
        return {}
    elif isinstance(value, dict):
        return value

    raise StxError(
        f'Unsupported arguments for function {call.key}.', call.location)


def check_unknown_options(options: Union[dict, Value], call: FunctionCall):
    if isinstance(options, dict):
        unknown_options = options.keys()

        if len(unknown_options) > 0:
            raise StxError(f'Unknown options for function {see(call.key)}:'
                           f' {see(unknown_options)}.')
    elif isinstance(options, Value):
        options_any = options.to_any()

        if options_any is not None:
            raise StxError(f'Unknown options for function {see(call.key)}:'
                           f' {see(options_any)}.', call.location)
    else:
        raise StxError(f'Unknown options for function {see(call.key)}.')


def make_plain_text(component: Component) -> str:
    if component.is_rich():
        logger.warning(
            'Rich component was converted to plain text.', component.location)

    return component.get_text()


def make_component_list(component: Component) -> List[Component]:
    if isinstance(component, Composite):
        return component.components
    elif isinstance(component, Paragraph):
        return component.contents

    return [component]