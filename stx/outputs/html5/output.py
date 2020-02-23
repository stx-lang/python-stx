from stx.document import Document, OutputTask
from stx.outputs.html5.serializer import document_to_html
from stx.utils.files import resolve_sibling


def renderer(output: OutputTask):
    html = document_to_html(output.document)

    with output.target.open() as f:
        for tag in html:
            tag.render(f)

    # TODO implement pretty-print
