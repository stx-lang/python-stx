from __future__ import annotations

import os
import string
from typing import Optional, List, Tuple

from stx.utils.stack import Stack
from stx.design.components import Composite, Component, TextBlock, Heading, \
    RawText, CodeBlock, Table, Figure, ListBlock, TableRow, StyledText, \
    LinkText, PlainText, ContentBox
from stx.design.document import Document
from stx.utils.files import resolve_sibling, walk_files
from ._directives import process_directive

from ._source import Source
from ._tape import Tape
from ._composer import Composer
from . import _marks


def parse_styled_text(tape: Tape, stop_marks: Stack) -> Optional[StyledText]:
    begin_location = tape.source.location

    if tape.test('*'):
        style = 'strong'
    elif tape.test('_'):
        style = 'emphasized'
    elif tape.test('`'):
        style = 'code'
    else:
        return None

    delimiter = tape.read()

    stop_marks.push(delimiter)

    contents = parse_inline_text(tape, stop_marks)

    stop_marks.pop()

    if not tape.pull(delimiter):
        raise tape.source.error(f'Styled text `{style}` was not closed (started at {begin_location.position}).')

    return StyledText(contents, style)


def parse_link_text(tape: Tape, stop_marks: Stack) -> Optional[LinkText]:
    if not tape.pull('['):
        return None

    stop_marks.push(']')

    contents = parse_inline_text(tape, stop_marks)

    stop_marks.pop()

    if not tape.pull(']'):
        raise Exception('link not closed')

    if tape.pull('('):
        reference = ''

        while not tape.test(')'):
            reference += tape.read()

        if not tape.pull(')'):
            raise Exception('reference not closed')
    else:
        reference = None

    return LinkText(contents, reference)


def parse_plain_text(tape: Tape, stop_marks: Stack) -> Optional[PlainText]:
    content = ''

    while tape.alive():
        if tape.test(stop_marks.peek()):
            break
        elif tape.any('*', '_', '`', '['):
            break
        elif tape.pull('\\'):
            if tape.test(stop_marks.peek()):
                content += tape.read()
            elif tape.any('*', '_', '`', '[', ']', '(', ')', '\\'):
                content += tape.read()
            else:
                content += '\\'
        else:
            content += tape.read()

    if len(content) == 0:
        return None

    return PlainText(content)


def parse_inline_text(tape: Tape, stop_marks: Stack) -> List[Component]:
    contents = []

    while tape.alive():
        if tape.test(stop_marks.peek()):
            break

        content = (parse_styled_text(tape, stop_marks)
                   or parse_link_text(tape, stop_marks)
                   or parse_plain_text(tape, stop_marks))

        if content is not None:
            contents.append(content)

    return contents


def parse_text_block(document: Document, source: Source, composer: Composer, stop_mark: Optional[str]):
    stop_marks = Stack()

    if stop_mark is not None:
        stop_marks.push(stop_mark)

    with Tape(source) as tape:
        components = parse_inline_text(tape, stop_marks)

    if len(components) == 0:
        composer.push_separator()
    else:
        composer.push(TextBlock(components))


def parse_heading_block(document: Document, source: Source, level: int, composer: Composer):
    content = parse_component(document, source)

    composer.push(Heading(content, level))


def process_include(document: Document, source: Source, include_paths: list, composer: Composer):
    for include_path in include_paths:
        target_path = resolve_sibling(source.file_path, include_path)
        file_paths = []

        if os.path.isdir(target_path):
            for file_path in walk_files(target_path):
                file_paths.append(file_path)
        else:
            file_paths.append(target_path)

        for file_path in sorted(file_paths):
            print(f'Processing: {file_path}...')
            if file_path.endswith('.stx'):
                with open(file_path, 'r') as stream:
                    source = Source(stream, file_path)

                    component = parse_component(document, source)

                    composer.push(component)
            else:
                # TODO add support for more extensions
                with open(file_path, 'r', encoding='UTF-8') as f:
                    content = f.read()

                composer.push(RawText(content))


def parse_name_values(tape: Tape) -> Tuple[str, List[str]]:
    tape.skip(' ')

    if not tape.test(string.ascii_letters):
        raise tape.source.error('Expected to read a name.')

    name = tape.read()

    while tape.test(string.ascii_letters + string.digits + '._-'):
        name += tape.read()

    tape.skip(' ')

    values = []

    if tape.pull('['):
        tape.skip(' ')

        value = ''

        while tape.alive():
            if tape.test(']'):
                break
            elif tape.pull(','):
                values.append(value)
                value = ''

                tape.skip(' ')
            elif tape.pull('\\'):
                c = tape.read()

                if c not in [',', ']']:
                    value += '\\'

                value += c
            else:
                value += tape.read()

        if not tape.pull(']'):
            raise tape.source.error('Expected to read a `]`')

        if value:
            values.append(value)

    tape.skip(' \n')

    if tape.alive():
        raise tape.source.error('Unexpected content')

    return name, values


def parse_directive(document: Document, source: Source, composer: Composer):
    with Tape(source) as tape:
        name, values = parse_name_values(tape)

        if name == 'include':
            process_include(document, source, values, composer)
        else:
            process_directive(name, values, document, source, composer)


def parse_attribute(document: Document, source: Source, composer: Composer):
    with Tape(source) as tape:
        name, values = parse_name_values(tape)

        composer.push_attribute(name, values)


def parse_code_block(document: Document, source: Source, composer: Composer):
    line = source.pop_line()

    flavor = line.get_current_text()

    lines = []

    begin_index = source.peek_begin_index()

    while True:
        line = source.pop_line()

        if line.test_current_text(_marks.code_block_mark):
            break

        lines.append(line.raw_text[begin_index:])

    composer.push(CodeBlock('\n'.join(lines), flavor))


def parse_pre_caption(document: Document, source: Source, composer: Composer):
    composer.pending_caption = parse_component(document, source)


def parse_post_caption(document: Document, source: Source, composer: Composer):
    caption = parse_component(document, source)

    last = None

    while len(composer.contents) > 0:
        last = composer.get_last_content()

        if last is not None:
            break

        composer.contents.pop()

    if isinstance(last, Table):
        last.caption = caption
    else:
        content = composer.pop()

        figure = Figure(content, caption)

        composer.push(figure)


def parse_list_item(document: Document, source: Source, composer: Composer, ordered: bool):
    last = composer.get_last_content()

    if isinstance(last, Figure):
        last = last.content

    if isinstance(last, ListBlock) and last.ordered == ordered:
        active_list = last
    else:
        active_list = ListBlock([], ordered)

        composer.push(active_list)

    content = parse_component(document, source)

    active_list.items.append(content)


def parse_table_row(document: Document, source: Source, composer: Composer, header: bool):
    last = composer.get_last_content()

    if isinstance(last, Table):
        active_table = last
    else:
        active_table = Table([])

        composer.push(active_table)

    cells = []

    stop_mark = _marks.table_cell_mark

    while True:
        cell = parse_component(document, source, stop_mark)

        cells.append(cell)

        line = source.try_line()

        if line is None:
            break
        elif not line.get_current_text().startswith(stop_mark):
            break

        line.indentation += len(stop_mark)

    active_table.rows.append(TableRow(cells, header))


def merge_component(base: Optional[Component], component: Component) -> Component:
    if base is None:
        return component
    elif isinstance(base, Composite):
        base.components.append(component)

    return Composite([base, component])


def parse_content_box(document: Document, source: Source, composer: Composer):
    content = parse_component(document, source)

    box = ContentBox(content)

    composer.consume_attributes(box)

    box.type = box.attributes.get_value('type')

    composer.push(box)


def parse_component(document: Document, source: Source, stop_mark: Optional[str] = None) -> Component:
    composer = Composer()

    while source.is_alive():
        line = source.get_line()

        if stop_mark and line.get_current_text().startswith(stop_mark):
            break

        block_mark = line.consume_block_info()

        if block_mark is None:
            parse_text_block(document, source, composer, stop_mark)
        else:
            is_flat = block_mark in _marks.flat_block_marks

            if not is_flat:
                source.push_begin_index(line.indentation)

            if block_mark in _marks.heading_marks:
                parse_heading_block(document, source, _marks.get_heading_level(block_mark), composer)
            elif block_mark == _marks.directive_mark:
                parse_directive(document, source, composer)
            elif block_mark == _marks.attribute_mark:
                parse_attribute(document, source, composer)
            elif block_mark == _marks.code_block_mark:
                parse_code_block(document, source, composer)
            elif block_mark == _marks.pre_caption_mark:
                parse_pre_caption(document, source, composer)
            elif block_mark == _marks.post_caption_mark:
                parse_post_caption(document, source, composer)
            elif block_mark == _marks.unordered_list_item_mark:
                parse_list_item(document, source, composer, False)
            elif block_mark == _marks.ordered_list_item_mark:
                parse_list_item(document, source, composer, True)
            elif block_mark == _marks.table_d_row_mark:
                parse_table_row(document, source, composer, False)
            elif block_mark == _marks.table_h_row_mark:
                parse_table_row(document, source, composer, False)
            elif block_mark == _marks.content_box_mark:
                parse_content_box(document, source, composer)
            else:
                raise source.error(f'Not implemented block mark: {block_mark}')

            if not is_flat:
                source.pop_begin_index()

    components = composer.compile()

    if len(components) == 1:
        return components[0]

    return Composite(components)
