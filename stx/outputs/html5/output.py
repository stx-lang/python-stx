from stx.document import Document
from stx.outputs.html5.serializer import document_to_html
from stx.outputs.output_task import OutputTask
from stx.utils.files import resolve_sibling


def renderer(document: Document, output: OutputTask):
    html = document_to_html(document)

    file_path = resolve_sibling(document.source_file, output.file)

    with open(file_path, 'w') as f:
        for tag in html:
            tag.render(f)

    # TODO implement pretty-print
