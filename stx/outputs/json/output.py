import json
from typing import TextIO

from stx.outputs.json.serializer import document_to_json
from stx.outputs.output_action import OutputAction


class JsonOutputAction(OutputAction):

    def dump(self, out: TextIO):
        d = document_to_json(self.document)

        # TODO implement options
        # if output.options.to_dict():
        indent = 2
        # else:
            # indent = None

        json.dump(d, out, indent=indent)
