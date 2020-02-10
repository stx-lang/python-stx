import json
from typing import TextIO

from stx.design.document import Document
from stx.rendering.json.serializer import document_to_json


def render_to_output(document: Document, output: TextIO):
    d = document_to_json(document)

    json.dump(d, output, indent=2)


def render_to_file(document: Document, file_path: str):
    with open(file_path, 'w') as output:
        render_to_output(document, output)
