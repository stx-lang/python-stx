from typing import Any

from stx.themes.built_in.classic_html import classic_theme

_themes = {}


def register_theme(name: str, output_format: str, theme: Any, override=False):
    key = f'{name}/{output_format}'

    if not override and key in _themes:
        raise Exception(f'Theme is already registered: {name}')

    _themes[key] = theme


def get_theme(name: str, output_format: str) -> Any:
    key = f'{name}/{output_format}'

    if key not in _themes:
        raise Exception(f'Theme `{name}` not found for '
                        f'the `{output_format}` format.')

    return _themes[key]


register_theme('classic', 'html', classic_theme)
