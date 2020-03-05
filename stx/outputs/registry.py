from typing import Dict, Type

from stx import logger
from stx.compiling.reading.location import Location
from stx.data_notation.values import Value, Empty
from stx.document import Document
from stx.outputs.html5.output import HtmlOutputAction
from stx.outputs.json.output import JsonOutputAction
from stx.outputs.output_action import OutputAction, OutputStdOut
from stx.outputs.output_action import OutputTarget
from stx.utils.stx_error import StxError
from stx.utils.debug import see

_handler_types: Dict[str, Type[OutputAction]] = {}


def register_type(
        format_key: str, handler_type: Type[OutputAction], override=False):
    if not override and format_key in _handler_types:
        raise StxError(f'Output handler already registered: {format_key}')

    _handler_types[format_key] = handler_type


def get_type(format_key: str) -> Type[OutputAction]:
    if format_key not in _handler_types:
        raise StxError(f'Format not supported: {format_key}')
    return _handler_types[format_key]


def make_output_action(
        document: Document,
        location: Location,
        arguments: Value) -> OutputAction:
    format_value = arguments.try_token()

    if format_value is not None:
        actual_format = format_value.to_str()
        actual_target = OutputStdOut()
        actual_options = Empty()
    else:
        args_map = arguments.to_map()

        format_value = args_map.pop('format', None)
        target_value = args_map.pop('target', None)
        options_value = args_map.pop('options', None)

        if len(args_map) > 0:
            for unknown_key in args_map.keys():
                logger.warning(
                    f'Unknown output argument: {see(unknown_key)}',
                    location)

        if format_value is not None:
            actual_format = format_value.to_str()
        else:
            raise StxError('Expected output format.', location)

        if target_value is not None:
            actual_target = OutputTarget.make(
                document, target_value.to_str())
        else:
            actual_target = OutputStdOut()

        if options_value is not None:
            actual_options = options_value
        else:
            actual_options = Empty()

    handler_type = get_type(actual_format)

    return handler_type(
        document=document,
        location=location,
        format_key=actual_format,
        target=actual_target,
        options=actual_options,
    )


# Built-in renderers
register_type('html', HtmlOutputAction)
register_type('json', JsonOutputAction)