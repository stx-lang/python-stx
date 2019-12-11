from os import path, walk
from typing import Optional, List

from stx.compiling.context import Context
from stx.compiling.raw_text import compile_paragraph
from stx.compiling.validator import build_links
from stx.components.blocks import Block, BComposite, BAttribute, BTitle, \
    BTableRow, BListItem, BTableCell, BSeparator, BCodeBlock, BLineText, \
    BElement, BDirective
from stx.components.content import CContent, CList, CTable, CContainer, \
    CHeading, CListItem, CTableRow, CTableCell, CCodeBlock, CRawText, \
    CParagraph, CPlainText, WithCaption, CEmbeddedText
from stx.parsing.block import parse
from stx.reader import Reader
from stx.utils import Stack


def from_file(context: Context, file_path: str, encoding='UTF-8') -> CContent:
    dir_path = path.dirname(file_path)

    context.base_path = dir_path
    context.encoding = encoding

    reader = Reader.from_file(file_path, encoding)

    return from_reader(context, reader)


def from_reader(context: Context, reader: Reader) -> CContent:
    block = parse(reader, Stack())
    content = compile_block(context, block)

    build_links(context, content)

    return content


def compile_block(context: Context, block: Block) -> CContent:
    if isinstance(block, BComposite):
        blocks = block.blocks
    else:
        blocks = [block]

    return compile_blocks(context, blocks)


def compile_title(context: Context, title: BTitle) -> CHeading:
    return CHeading(
        content=compile_block(context, title.content),
        level=title.level,
    )


def compile_list_item(context: Context, item: BListItem) -> CListItem:
    return CListItem(
        content=compile_block(context, item.content),
    )


def compile_table_cell(context: Context, cell: BTableCell) -> CTableCell:
    if isinstance(cell.content, BTitle):
        header = True
        block = cell.content.content
    else:
        header = False
        block = cell.content

    content = compile_block(context, block)

    return CTableCell(content, header)


def compile_table_row(context: Context, row: BTableRow) -> CTableRow:
    return CTableRow(
        cells=[compile_table_cell(context, cell) for cell in row.cells],
    )


def compile_code_block(
        context: Context,
        code: BCodeBlock,
        caption: Optional[CContent] = None) -> CCodeBlock:
    return CCodeBlock(
        text=code.text,
        caption=caption,
    )


def compile_composite(context: Context, composite: BComposite) -> CContent:
    return compile_blocks(context, composite.blocks)


def compile_include(context: Context, include_path: str) -> Optional[CContent]:
    file_paths = []
    target_path = path.join(context.base_path, include_path)

    if path.isdir(target_path):
        for root, dirs, files in walk(target_path):
            for name in files:
                file_paths.append(path.join(root, name))
    else:
        file_paths.append(target_path)

    contents = []

    for file_path in sorted(file_paths):
        if file_path.endswith('.stx'):
            reader = context.resolve_reader(file_path)
            content = from_reader(context, reader)

            contents.append(content)
        else:
            source = path.relpath(file_path, context.base_path)

            with open(file_path, 'r', encoding='UTF-8') as f:
                content = f.read()

            contents.append(CEmbeddedText(content, source))

    if len(contents) == 0:
        return None
    elif len(contents) == 1:
        return contents[0]

    return CContainer(contents)


def compile_stylesheet(context: Context, stylesheet_path: str):
    context.linked_stylesheets.append(stylesheet_path)


def compile_directive(
        context: Context, directive: BDirective) -> Optional[CContent]:
    if directive.name == 'include':
        if len(directive.values) != 1:
            raise Exception('Expected one argument')
        return compile_include(context, directive.values[0])
    elif directive.name == 'stylesheet':
        if len(directive.values) != 1:
            raise Exception('Expected one argument')
        compile_stylesheet(context, directive.values[0])
        return None

    raise Exception(f'directive not implemented: {directive.name}')


def compile_blocks(context: Context, blocks: List[Block]) -> CContent:
    active_list: Optional[CList] = None
    active_table: Optional[CTable] = None
    active_raw: Optional[CRawText] = None
    active_attrs: Optional[dict] = None

    pending_caption = None

    def caption_validation():
        if pending_caption is not None:
            raise Exception('floating caption')

    contents = []

    for block in blocks:
        reset_list = True
        reset_table = True
        reset_raw = True
        validate_caption = True

        if isinstance(block, BTitle):
            heading = compile_title(context, block)
            heading.attributes = active_attrs
            active_attrs = None

            contents.append(heading)
        elif isinstance(block, BListItem):
            if (active_list is not None
                    and active_list.ordered != block.ordered):
                active_list = None

            item = compile_list_item(context, block)

            if active_list is None:
                active_list = CList([item], block.ordered)
                active_list.attributes = active_attrs
                active_attrs = None

                contents.append(active_list)
            else:
                active_list.items.append(item)

            reset_list = False
        elif isinstance(block, BElement):
            if block.mark == '>':
                pending_caption = compile_block(context, block.content)
            elif block.mark == '<':
                post_caption = compile_block(context, block.content)

                if len(contents) == 0:
                    raise Exception('no element to put caption')

                last_content = contents[-1]

                if not isinstance(last_content, WithCaption):
                    raise Exception('element cannot have caption')

                last_content.caption = post_caption
            else:
                raise NotImplementedError(f'not implemented mark {block.mark}')

            validate_caption = False
        elif isinstance(block, BTableRow):
            row = compile_table_row(context, block)

            if active_table is None:
                active_table = CTable([row], caption=pending_caption)
                active_table.attributes = active_attrs
                active_attrs = None

                pending_caption = None

                contents.append(active_table)
            else:
                active_table.rows.append(row)

            reset_table = False
        elif isinstance(block, BSeparator):
            reset_list = block.size >= 2
            reset_table = block.size >= 2
            reset_raw = block.size >= 1
        elif isinstance(block, BCodeBlock):
            code_block = compile_code_block(context, block, pending_caption)
            code_block.attributes = active_attrs
            active_attrs = None

            pending_caption = None

            contents.append(code_block)
        elif isinstance(block, BLineText):
            if active_raw is None:
                active_raw = CRawText([block.text])

                contents.append(active_raw)
            else:
                active_raw.lines.append(block.text)

            reset_raw = False
        elif isinstance(block, BAttribute):
            if active_attrs is None:
                active_attrs = {}

            if block.name in active_attrs:
                raise Exception(f'Attribute already defined: {block.name}')

            active_attrs[block.name] = block.values
        elif isinstance(block, BDirective):
            content = compile_directive(context, block)

            if content is not None:
                contents.append(content)
        else:
            raise NotImplementedError()

        if reset_list:
            active_list = None

        if reset_table:
            active_table = None

        if reset_raw:
            active_raw = None

        if validate_caption:
            caption_validation()

    caption_validation()

    for i in range(0, len(contents)):
        if isinstance(contents[i], CRawText):
            contents[i] = compile_paragraph('\n'.join(contents[i].lines))

    if len(contents) == 1:
        return contents[0]

    return CContainer(contents)
