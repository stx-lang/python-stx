from __future__ import annotations

from io import TextIOWrapper
from typing import Optional, List

from stx.components import Component

import sys
from typing import Optional, TextIO

from stx import logger
from stx.compiling.reading.location import Location
from stx.data_notation.values import Value, Empty
from stx.utils.files import resolve_sibling
from stx.utils.stx_error import StxError
from stx.utils.debug import see


class OutputTarget:

    @staticmethod
    def make(document: Document, target: str) -> OutputTarget:
        # TODO add more targets

        file_path = resolve_sibling(
            document.source_file, target)

        return OutputFile(file_path)

    def open(self) -> TextIO:
        # TODO add encoding as argument
        raise NotImplementedError()


class OutputFile(OutputTarget):

    def __init__(self, file_path: str):
        self.file_path = file_path

    def open(self) -> TextIO:
        return open(self.file_path, mode='w')


class OutputTerminal(OutputTarget):

    def open(self) -> TextIO:
        raise NotImplementedError()  # TODO


class OutputTask:

    def __init__(
            self, document: Document, location: Location, arguments: Value):
        self.document = document
        self.location = location

        format_value = arguments.try_token()

        if format_value is not None:
            actual_format = format_value.to_str()
            actual_target = OutputTerminal()
            actual_options = Empty()
        else:
            args_map = arguments.to_map()

            format_value = args_map.pop('format', None)
            target_value = args_map.pop('target', None)
            options_value = args_map.pop('options', None)

            if len(args_map) > 0:
                for unknown_key in args_map.keys():
                    logger.warning(
                        f'Unknown output argument: {see(unknown_key)}',
                        location)

            if format_value is not None:
                actual_format = format_value.to_str()
            else:
                raise StxError('Expected output format.', location)

            if target_value is not None:
                actual_target = OutputTarget.make(
                    document, target_value.to_str())
            else:
                actual_target = OutputTerminal()

            if options_value is not None:
                actual_options = options_value
            else:
                actual_options = Empty()

        self.format: str = actual_format
        self.target: OutputTarget = actual_target
        self.options: Value = actual_options


class Document:

    def __init__(self, source_file):
        self.source_file = source_file
        self.title: Optional[str] = None
        self.author: Optional[str] = None
        self.format: Optional[str] = None
        self.encoding: Optional[str] = None
        self.header: Optional[Component] = None
        self.content: Optional[Component] = None
        self.footer: Optional[Component] = None
        self.stylesheets: List[str] = []
        self.outputs: List[OutputTask] = []
