import json

from stx.document import Document, OutputTask
from stx.outputs.json.serializer import document_to_json
from stx.utils.files import resolve_sibling


def renderer(output: OutputTask):
    d = document_to_json(output.document)

    # TODO implement options
    # if output.options.to_dict():
    indent = 2
    # else:
        # indent = None

    with output.target.open() as f:
        json.dump(d, f, indent=indent)
