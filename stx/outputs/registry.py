from typing import Any, Callable, Dict

from stx.document import Document
from stx.outputs.output_task import OutputTask
from stx.outputs.html5.output import renderer as html_renderer
from stx.outputs.json.output import renderer as json_renderer
from stx.utils.stx_error import StxError


RendererType = Callable[[Document, OutputTask], Any]


_renderers: Dict[str, RendererType] = {
    # Built-in renderers
    'html': html_renderer,
    'json': json_renderer,
}


def register_renderer(
        format_key: str, renderer: RendererType, override=False):
    if not override and format_key in _renderers:
        raise StxError(f'Renderer already registered: {format_key}')

    _renderers[format_key] = renderer


def get_renderer(format_key: str) -> RendererType:
    if format_key not in _renderers:
        raise StxError(f'Format not supported: {format_key}')
    return _renderers[format_key]
