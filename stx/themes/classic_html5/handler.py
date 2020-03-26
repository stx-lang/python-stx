import os

from stx.outputs.html.themes import HtmlTheme


def load_asset(file: str) -> str:
    root = os.path.dirname(__file__)

    with open(f'{root}/assets/{file}', mode='r') as f:
        return f.read()


classic_theme = HtmlTheme()

classic_theme.head_styles.extend([
    load_asset('layout.css'),
    load_asset('style.css'),
])

classic_theme.body_scripts.extend([
    load_asset('jquery-3.4.1.min.js'),
    load_asset('create-layout.js'),
    load_asset('toc-links.js'),
])
