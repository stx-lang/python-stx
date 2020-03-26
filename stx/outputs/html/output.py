from typing import TextIO

from stx.outputs.html.serializer import document_to_html
from stx.outputs.html.themes import HtmlTheme, NullHtmlTheme
from stx.outputs.output_action import OutputAction
from stx.themes.registry import get_theme


class HtmlOutputAction(OutputAction):

    def dump(self, out: TextIO):
        if self.theme is not None:
            theme = get_theme(self.theme, self.format_key)

            if not isinstance(theme, HtmlTheme):
                raise Exception(f'Theme `{self.theme}` is not '
                                f'compatible with `{self.format_key}`.')
        else:
            theme = NullHtmlTheme()

        html = document_to_html(self.document, theme)

        for tag in html:
            tag.render(out)

        # TODO implement pretty-print
