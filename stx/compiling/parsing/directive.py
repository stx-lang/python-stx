from abc import ABC
from typing import Any

from stx.compiling.reading.location import Location
from stx.components import RawText, TableOfContents
from stx.compiling.parsing.abstract import AbstractParser
from stx.compiling.values import parse_entry
from stx.utils.converter import to_list_str, to_str
from stx.utils.files import resolve_include_files
from stx.utils.stx_error import StxError


class DirectiveParser(AbstractParser, ABC):

    def parse_directive(self, location: Location):
        content = self.get_content()
        file_path = content.file_path

        key, value = parse_entry(content)

        if content.column > 0:
            content.expect_end_of_line()

        if key == 'title':
            self.document.title = to_str(value)
        elif key == 'author':
            self.document.author = to_str(value)
        elif key == 'format':
            self.document.format = to_str(value)
        elif key == 'encoding':
            self.document.encoding = to_str(value)
        elif key == 'toc':
            self.composer.add(TableOfContents(location))
        elif key == 'stylesheets':
            self.document.stylesheets = to_list_str(value)
        elif key == 'include':
            self.process_import(location, file_path, value, parse=True)
        elif key == 'embed':
            self.process_import(location, file_path, value, parse=False)
        else:
            raise StxError(f'Unsupported directive: {key}')

    def process_import(
            self,
            location: Location,
            file_path: str,
            include_path: Any,
            parse: bool):
        if not isinstance(include_path, str):
            raise StxError('Expected a string.')

        file_paths = resolve_include_files(include_path, file_path)

        if parse:
            self.push_files(file_paths)
        else:
            for file_path in file_paths:
                with open(file_path, 'r', encoding='UTF-8') as f:
                    text = f.read()

                # TODO add support for more type of files
                self.composer.add(RawText(location, text))
