from io import StringIO
from typing import Optional, Union, List

from stx import logger
from stx.components import FunctionCall, Component, Literal, Composite
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


def make_component_list_arg(call: FunctionCall) -> List[Component]:
    if call.plain_text_arg is not None:
        component_list_arg_must_be_none(call)

        logger.warning(
            f'The expected argument for function {call.key} should be'
            f' rich text instead of plain text.', call.location
        )

        return [Literal(call.location, call.plain_text_arg)]
    else:
        plain_text_arg_must_be_none(call)

        return component_list_arg_must_be_present(call)


def make_component_arg(call: FunctionCall) -> Component:
    components = make_component_list_arg(call)

    if len(components) == 1:
        return components[0]

    return Composite(call.location, components)


def make_literal_arg(call: FunctionCall) -> str:
    if call.plain_text_arg is not None:
        component_list_arg_must_be_none(call)

        return call.plain_text_arg
    else:
        plain_text_arg_must_be_none(call)

        components = component_list_arg_must_be_present(call)

        logger.warning(
            f'The expected argument for function {call.key} should be'
            f' plain text instead of rich text.', call.location
        )

        out = StringIO()

        for component in components:
            component.write_text(out)

        return out.getvalue()


def component_list_arg_must_be_none(call: FunctionCall):
    if call.components_arg is not None:
        raise StxError(
            f'Captured content is not allowed as '
            f'argument for function {see(call.key)}.', call.location)


def plain_text_arg_must_be_none(call: FunctionCall):
    if call.plain_text_arg is not None:
        raise StxError(
            f'Literal content is not allowed as '
            f'argument for function {see(call.key)}.', call.location)


def component_list_arg_must_be_present(call: FunctionCall) -> List[Component]:
    if call.components_arg is None:
        raise StxError(
            f'Captured content must be passed as '
            f'argument for function {see(call.key)}.', call.location)

    return call.components_arg


def component_arg_must_be_present(call: FunctionCall) -> Component:
    if call.components_arg is None:
        raise StxError(
            f'Captured content must be passed as '
            f'argument for function {see(call.key)}.', call.location)

    if len(call.components_arg) == 1:
        return call.components_arg[0]

    return Composite(call.location, call.components_arg)


def plain_text_arg_must_be_present(call: FunctionCall) -> str:
    if call.plain_text_arg is None:
        raise StxError(
            f'Literal content must be passed as '
            f'argument for function {see(call.key)}.', call.location)

    return call.plain_text_arg


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
