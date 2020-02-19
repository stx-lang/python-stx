from typing import Callable, Dict, Optional

from stx.compiling.processing.macros.image import process_image
from stx.compiling.reading.location import Location
from stx.components import Component
from stx.data_notation.values import Value
from stx.document import Document
from stx.utils.stx_error import StxError


MacroType = Callable[[Document, Location, Value], Component]


_macros: Dict[str, MacroType] = {
    # Built-in macros
    'img': process_image,
    'image': process_image,
}


def register_macro(
        macro_key: str, renderer: MacroType, override=False):
    if not override and macro_key in _macros:
        raise StxError(f'Macro already registered: {macro_key}')

    _macros[macro_key] = renderer


def get_macro(macro_key: str) -> Optional[MacroType]:
    if macro_key not in _macros:
        return None
    return _macros[macro_key]
