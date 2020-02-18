import json

from stx.document import Document
from stx.outputs.json.serializer import document_to_json
from stx.outputs.output_task import OutputTask
from stx.utils.files import resolve_sibling


def renderer(document: Document, output: OutputTask):
    d = document_to_json(document)

    if output.pretty:
        indent = 2
    else:
        indent = None

    file_path = resolve_sibling(document.source_file, output.file)

    with open(file_path, 'w') as f:
        json.dump(d, f, indent=indent)
