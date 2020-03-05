from typing import Callable, Dict, Optional

from stx.compiling.resolvers.built_in import resolve_code, \
    resolve_custom_style, resolve_toc, resolve_embed
from stx.compiling.resolvers.built_in import resolve_image
from stx.compiling.resolvers.built_in import resolve_warning
from stx.compiling.resolvers.built_in import resolve_admonition
from stx.compiling.resolvers.built_in import resolve_line_feed

from stx.components import Component, FunctionCall

from stx.document import Document
from stx.utils.stx_error import StxError


ResolverType = Callable[[Document, FunctionCall], Component]


_resolvers: Dict[str, ResolverType] = {}


def register_resolver(
        function_key: str, resolver: ResolverType, override=False):
    if not override and function_key in _resolvers:
        raise StxError(f'Macro already registered: {function_key}')

    _resolvers[function_key] = resolver


def get_resolver(macro_key: str) -> Optional[ResolverType]:
    if macro_key not in _resolvers:
        return None
    return _resolvers[macro_key]


# Built-in

register_resolver('img', resolve_image)
register_resolver('image', resolve_image)
register_resolver('code', resolve_code)
register_resolver('warning', resolve_warning)
register_resolver('admonition', resolve_admonition)
register_resolver('br', resolve_line_feed)
register_resolver('style', resolve_custom_style)
register_resolver('toc', resolve_toc)
register_resolver('embed', resolve_embed)
