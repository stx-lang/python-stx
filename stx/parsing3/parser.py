from io import StringIO
from typing import Any, Optional

from stx.components import Component, Composite, Separator, Section, \
    PlainText, Placeholder, CodeBlock, ContentBox, Table, TableRow, RawText, \
    Figure, ListBlock
from stx.design.document import Document
from stx.parsing._marks import heading1_mark, heading_marks, get_section_level, \
    directive_mark, attribute_mark, code_block_mark, content_box_mark, \
    table_h_row_mark, table_d_row_mark, table_cell_mark, pre_caption_mark, \
    post_caption_mark, ordered_list_item_mark, unordered_list_item_mark
from stx.parsing3.composer import Composer
from stx.parsing3.source import Source
from stx.parsing3.values import parse_entry, parse_name, NAME_BEGIN_CHARS
from stx.utils.files import resolve_include_files
from stx.utils.stx_error import StxError


def parse_paragraph(doc: Document, text: str, composer: Composer):
    composer.add(PlainText(text))  # TODO parse styled text


def parse_section(
        doc: Document,
        source: Source,
        composer: Composer,
        level: int,
        mark_indentation: int,
        root_indentation: int):
    section = Section(None, None, level)

    composer.add(section)

    section.heading = parse_component(doc, source, composer, mark_indentation)
    section.content = parse_component(
        doc, source, composer, root_indentation, parent_section=section)


def process_include(
        doc: Document,
        source: Source,
        composer: Composer,
        value: Any):
    if isinstance(value, list):
        include_paths = value
    elif isinstance(value, str):
        include_paths = [value]
    else:
        raise StxError('Expected a string or a list of strings.')

    for include_path in include_paths:
        file_paths = resolve_include_files(include_path, source.file_path)

        for file_path in file_paths:
            print(f'Processing: {file_path}...')
            if file_path.endswith('.stx'):
                with Source.from_file(file_path) as include_source:
                    component = parse_component(
                        doc, include_source, composer, indentation=0, breakable=False)

                    composer.add(component)
            else:
                # TODO add support for more extensions
                with open(file_path, 'r', encoding='UTF-8') as f:
                    content = f.read()

                composer.add(RawText(content))


def parse_directive(doc: Document, source: Source, composer: Composer):
    key, value = parse_entry(source)

    if key == 'title':
        if not isinstance(value, str):
            raise StxError('Expected a string for the title')

        doc.title = value
    elif key == 'author':
        if not isinstance(value, str):
            raise StxError('Expected a string for the author')

        doc.author = value
    elif key == 'format':
        if not isinstance(value, str):
            raise StxError('Expected a string for the format')

        doc.format = value
    elif key == 'toc':
        composer.add(Placeholder('toc'))
    elif key == 'link':
        # TODO handle links
        pass
    elif key == 'include':
        process_include(doc, source, composer, value)
    else:
        raise StxError(f'Unsupported directive: {key}')

    if source.column > 0:
        source.expect_end_of_line()

    source.skip_empty_line()


def parse_attribute(doc: Document, source: Source, composer: Composer):
    key, value = parse_entry(source)

    source.expect_end_of_line()
    source.skip_empty_line()

    composer.push_attribute(key, value)


def parse_code_block(
        doc: Document,
        source: Source,
        composer: Composer,
        root_indentation: int):
    c = source.peek()

    if c in NAME_BEGIN_CHARS:
        lang = parse_name(source)
    else:
        lang = None

    source.expect_end_of_line()

    out = StringIO()

    while True:
        line = source.read_line(root_indentation)

        if line is None:
            raise StxError('Unexpected end of block.')
        elif line.strip() == code_block_mark:
            break

        out.write(line)

    code = out.getvalue()

    composer.add(CodeBlock(code, lang))


def parse_content_box(
        doc: Document,
        source: Source,
        composer: Composer,
        mark_indentation: int):
    box = ContentBox(None)  # TODO make empty constructors

    composer.add(box)

    box.content = parse_component(doc, source, composer, mark_indentation)


def parse_table_row(
        doc: Document,
        source: Source,
        composer: Composer,
        indentation: int,
        header: bool):
    table = composer.get_last_component()

    if not isinstance(table, Table):
        table = Table([])

        composer.add(table)

    row = TableRow([], header)

    table.rows.append(row)

    parse_table_cell(doc, source, composer, indentation)


def parse_table_cell(
        doc: Document,
        source: Source,
        composer: Composer,
        indentation: int):
    table = composer.get_last_component()

    if not isinstance(table, Table):
        table = Table([])

        composer.add(table)

    row = table.get_last_row()

    if row is None:
        row = TableRow([], False)

        table.rows.append(row)

    source.stop_mark = table_cell_mark

    cell = parse_component(doc, source, composer, indentation)

    source.stop_mark = None

    row.cells.append(cell)


def parse_pre_caption(
        doc: Document,
        source: Source,
        composer: Composer,
        mark_indentation: int):
    caption = parse_component(doc, source, composer, mark_indentation)

    composer.push_pre_caption(caption)


def parse_post_caption(
        doc: Document,
        source: Source,
        composer: Composer,
        indentation: int):
    caption = parse_component(doc, source, composer, indentation)

    composer.push_post_caption(caption)


def parse_list_item(
        doc: Document,
        source: Source,
        composer: Composer,
        indentation: int,
        ordered: bool):
    list_block = composer.get_last_component()

    if not isinstance(list_block, ListBlock):
        list_block = ListBlock([], ordered)

        composer.add(list_block)

    list_item = parse_component(doc, source, composer, indentation)

    list_block.items.append(list_item)


def parse_component(
        doc: Document,
        source: Source,
        composer: Composer,
        indentation: int,
        breakable=True,
        parent_section: Optional[Section] = None) -> Component:
    composer.push()

    while source.alive(indentation):
        source.checkout_position()
        mark = source.read_mark()

        if mark is None:
            source.commit_position()
            text = source.read_text(indentation=source.column)

            if len(text) > 0:
                parse_paragraph(doc, text, composer)
            elif breakable:
                break  # TODO
            else:
                composer.add(Separator())
        else:
            mark_indentation = source.column
            root_indentation = indentation

            if mark in heading_marks:
                section_level = get_section_level(mark)

                if parent_section is not None and section_level >= parent_section.level:
                    source.rollback_position()
                    break
                else:
                    source.commit_position()

                parse_section(
                    doc, source, composer, section_level,
                    mark_indentation, root_indentation)
            else:
                source.commit_position()

                if mark == directive_mark:
                    parse_directive(doc, source, composer)
                elif mark == attribute_mark:
                    parse_attribute(doc, source, composer)
                elif mark == code_block_mark:
                    parse_code_block(doc, source, composer, root_indentation)
                elif mark == content_box_mark:
                    parse_content_box(doc, source, composer, mark_indentation)
                elif mark == table_h_row_mark:
                    parse_table_row(
                        doc, source, composer, mark_indentation, header=True)
                elif mark == table_d_row_mark:
                    parse_table_row(
                        doc, source, composer, mark_indentation, header=True)
                elif mark == table_cell_mark:
                    parse_table_cell(doc, source, composer, mark_indentation)
                elif mark == pre_caption_mark:
                    parse_pre_caption(doc, source, composer, mark_indentation)
                elif mark == post_caption_mark:
                    parse_post_caption(doc, source, composer, mark_indentation)
                elif mark == unordered_list_item_mark:
                    parse_list_item(doc, source, composer, mark_indentation, False)
                elif mark == ordered_list_item_mark:
                    parse_list_item(doc, source, composer, mark_indentation, True)
                else:
                    raise StxError(f'Unsupported mark: `{mark}`')

    return composer.pop()


def parse_document(source: Source) -> Document:
    doc = Document()
    composer = Composer()

    doc.content = parse_component(
        doc, source, composer, indentation=0, breakable=False)

    return doc
