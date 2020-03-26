from stx import resources
from stx.outputs.html.themes import HtmlTheme


classic_theme = HtmlTheme()

classic_theme.head_styles.extend([
    resources.get_text('classic_html/layout.css'),
    resources.get_text('classic_html/style.css'),
])

classic_theme.body_scripts.extend([
    resources.get_text('classic_html/jquery-3.4.1.min.js'),
    resources.get_text('classic_html/create-layout.js'),
    resources.get_text('classic_html/toc-links.js'),
])
