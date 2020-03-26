import json
from typing import TextIO

from stx.outputs.json.serializer import document_to_json
from stx.outputs.output_action import OutputAction


class JsonOutputAction(OutputAction):

    def dump(self, out: TextIO):
        d = document_to_json(self.document)

        # TODO implement options
        indent = 2

        json.dump(d, out, indent=indent)
