from typing import Callable, Dict, Optional

from stx.functions.built_in import resolve_code
from stx.functions.built_in import resolve_custom_style
from stx.functions.built_in import resolve_toc
from stx.functions.built_in import resolve_embed
from stx.functions.built_in import resolve_image
from stx.functions.built_in import resolve_warning
from stx.functions.built_in import resolve_admonition
from stx.functions.built_in import resolve_line_feed
from stx.functions.built_in import resolve_information
from stx.functions.built_in import layout_function

from stx.components import Component, FunctionCall

from stx.document import Document
from stx.utils.stx_error import StxError


FunctionType = Callable[[Document, FunctionCall], Component]


_functions: Dict[str, FunctionType] = {}


def add(function_key: str, function: FunctionType, override=False):
    if not override and function_key in _functions:
        raise StxError(f'Function is already registered: {function_key}')

    _functions[function_key] = function


def get(function_key: str) -> Optional[FunctionType]:
    if function_key not in _functions:
        return None
    return _functions[function_key]


# Built-in

add('img', resolve_image)
add('image', resolve_image)
add('code', resolve_code)
add('warning', resolve_warning)
add('info', resolve_information)
add('information', resolve_information)
add('admonition', resolve_admonition)
add('br', resolve_line_feed)
add('style', resolve_custom_style)
add('toc', resolve_toc)
add('embed', resolve_embed)
add('layout', layout_function)
