from abc import ABC
from typing import Any

from stx.compiling.reading.location import Location
from stx.components import RawText, TableOfContents
from stx.compiling.parsing.abstract import AbstractParser
from stx.data_notation.parsing import parse_entry
from stx.data_notation.values import Value
from stx.outputs.output_task import OutputTask
from stx.utils.files import resolve_include_files
from stx.utils.stx_error import StxError


class DirectiveParser(AbstractParser, ABC):

    def parse_directive(self, location: Location):
        content = self.get_content()
        file_path = content.file_path

        entry = parse_entry(content)

        key = entry.name
        value = entry.value

        if content.column > 0:
            content.expect_end_of_line()

        if key == 'title':
            self.document.title = value.to_str()
        elif key == 'author':
            self.document.author = value.to_str()
        elif key == 'format':
            self.document.format = value.to_str()
        elif key == 'encoding':
            self.document.encoding = value.to_str()
        elif key == 'toc':
            self.composer.add(TableOfContents(location))
        elif key == 'stylesheets':
            self.document.stylesheets = value.to_list()
        elif key == 'include':
            self.process_import(location, file_path, value, parse=True)
        elif key == 'embed':
            self.process_import(location, file_path, value, parse=False)
        elif key == 'output':
            self.process_output(location, value)
        else:
            raise StxError(f'Unsupported directive: {key}')

    def process_import(
            self,
            location: Location,
            file_path: str,
            include_path: Value,
            parse: bool):
        file_paths = resolve_include_files(include_path.to_str(), file_path)

        if parse:
            self.push_files(file_paths)
        else:
            for file_path in file_paths:
                with open(file_path, 'r', encoding='UTF-8') as f:
                    text = f.read()

                # TODO add support for more type of files
                self.composer.add(RawText(location, text))

    def process_output(self, location: Location, value: Value):
        # TODO pass Value object directly
        self.document.outputs.append(OutputTask(location, value.to_dict()))
