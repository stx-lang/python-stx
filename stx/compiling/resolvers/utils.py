from io import StringIO
from typing import Optional

from stx.components import FunctionCall, Component, Literal
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


def make_content_arg(call: FunctionCall):
    # TODO add warning for forced conversion
    if call.literal_arg is not None:
        content_arg_must_be_none(call)

        return Literal(call.location, call.literal_arg)
    else:
        literal_arg_must_be_none(call)

        return content_arg_must_be_present(call)


def make_literal_arg(call: FunctionCall) -> str:
    # TODO add warning for forced conversion
    if call.literal_arg is not None:
        content_arg_must_be_none(call)

        return call.literal_arg
    else:
        literal_arg_must_be_none(call)

        content = content_arg_must_be_present(call)

        out = StringIO()

        content.write_text(out)

        return out.getvalue()


def content_arg_must_be_none(call: FunctionCall):
    if call.content_arg is not None:
        raise StxError(
            f'Captured content is not allowed as '
            f'argument for function {see(call.key)}.', call.location)


def literal_arg_must_be_none(call: FunctionCall):
    if call.literal_arg is not None:
        raise StxError(
            f'Literal content is not allowed as '
            f'argument for function {see(call.key)}.', call.location)


def content_arg_must_be_present(call: FunctionCall) -> Component:
    if call.content_arg is None:
        raise StxError(
            f'Captured content must be passed as '
            f'argument for function {see(call.key)}.', call.location)

    return call.content_arg


def literal_arg_must_be_present(call: FunctionCall) -> str:
    if call.content_arg is not None:
        raise StxError(
            f'Literal content must be passed as '
            f'argument for function {see(call.key)}.', call.location)

    return call.literal_arg


def options_must_be_empty(options: Value, call: FunctionCall):
    options_any = options.to_any()

    if options_any is not None:
        raise StxError(f'Unknown options for function {see(call.key)}:'
                       f' {see(options_any)}.')


def options_dict_must_be_empty(options: dict, call: FunctionCall):
    unknown_options = options.keys()

    if len(unknown_options) > 0:
        raise StxError(f'Unknown options for function {see(call.key)}:'
                       f' {see(unknown_options)}.')

