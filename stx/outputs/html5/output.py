from typing import TextIO

from stx.outputs.html5.serializer import document_to_html
from stx.outputs.output_action import OutputAction


class HtmlOutputAction(OutputAction):

    def dump(self, out: TextIO):
        html = document_to_html(self.document)

        for tag in html:
            tag.render(out)

        # TODO implement pretty-print
