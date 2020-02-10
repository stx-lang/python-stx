from typing import Any

from stx.components import Placeholder
from stx.components import RawText
from stx.parsing3.parsers.base import BaseParser
from stx.parsing3.source import Source
from stx.parsing3.values import parse_entry
from stx.utils.files import resolve_include_files
from stx.utils.stx_error import StxError


class DirectiveParser(BaseParser):

    def parse_directive(self):
        key, value = parse_entry(self.source)

        if key == 'title':
            if not isinstance(value, str):
                raise StxError('Expected a string for the title')

            self.document.title = value
        elif key == 'author':
            if not isinstance(value, str):
                raise StxError('Expected a string for the author')

            self.document.author = value
        elif key == 'format':
            if not isinstance(value, str):
                raise StxError('Expected a string for the format')

            self.document.format = value
        elif key == 'toc':
            self.composer.add(Placeholder('toc'))
        elif key == 'link':
            # TODO handle links
            pass
        elif key == 'include':
            self.process_include(value)
        else:
            raise StxError(f'Unsupported directive: {key}')

        if self.source.column > 0:
            self.source.expect_end_of_line()

        self.source.skip_empty_line()

    def process_include(self, value: Any):
        if isinstance(value, list):
            include_paths = value
        elif isinstance(value, str):
            include_paths = [value]
        else:
            raise StxError('Expected a string or a list of strings.')

        for include_path in include_paths:
            file_paths = resolve_include_files(include_path,
                                               self.source.file_path)

            for file_path in file_paths:
                print(f'Processing: {file_path}...')
                if file_path.endswith('.stx'):
                    with Source.from_file(file_path) as include_source:
                        self.source_stack.append(include_source)

                        # TODO push source
                        self.parse_components(
                            indentation=0,
                            breakable=False)

                        self.source_stack.pop()
                else:
                    # TODO add support for more extensions
                    with open(file_path, 'r', encoding='UTF-8') as f:
                        content = f.read()

                    self.composer.add(RawText(content))
