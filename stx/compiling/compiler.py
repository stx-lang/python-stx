from os import path, walk

from typing import List, Optional

from stx import logger
from stx.compiling.state import State
from stx.compiling.context import Context
from stx.components.blocks import Block, BComposite, BAttribute, BTitle
from stx.components.blocks import BTableRow, BListItem, BTableCell
from stx.components.blocks import MarkedBlock, BDirective
from stx.components.blocks import BSeparator, BCodeBlock, BLineText
from stx.components.content import CContent, CList, CTable, CContainer
from stx.components.content import CHeading, CListItem, CTableRow
from stx.components.content import CTableCell, CCodeBlock, CFigure
from stx.components.content import CEmbeddedText

from stx.parsing.block import parse
from stx.reader import Reader
from stx.utils import Stack


def from_file(context: Context, file_path: str, encoding='UTF-8') -> CContent:
    logger.info(f'Loading file {file_path}...')

    dir_path = path.dirname(file_path)

    context.base_path = dir_path
    context.encoding = encoding

    reader = Reader.from_file(file_path, encoding)

    return from_reader(context, reader)


def from_reader(context: Context, reader: Reader) -> CContent:
    logger.info('Parsing file...')

    block = parse(reader, Stack())

    logger.info('Compiling blocks...')
    content = compile_block(context, block)

    return content


def compile_block(context: Context, block: Block) -> CContent:
    if isinstance(block, BComposite):
        blocks = block.blocks
    else:
        blocks = [block]

    return compile_blocks(context, blocks)


def compile_blocks(context: Context, blocks: List[Block]) -> CContent:
    state = State()

    for block in blocks:
        if isinstance(block, BDirective):
            compile_directive(state, context, block)
        elif isinstance(block, BTitle):
            compile_title(state, context, block)
        elif isinstance(block, BListItem):
            compile_list_item(state, context, block)
        elif isinstance(block, BTableRow):
            compile_table_row(state, context, block)
        elif isinstance(block, BCodeBlock):
            compile_code_block(state, context, block)
        elif isinstance(block, MarkedBlock):
            if block.mark == '>':
                compile_pre_caption(state, context, block)
            elif block.mark == '<':
                compile_post_caption(state, context, block)
            else:
                raise NotImplementedError(
                    f'Not implemented mark {block.mark}')
        elif isinstance(block, BLineText):
            state.push_line(block.text)
        elif isinstance(block, BAttribute):
            state.push_attribute(block.name, block.values)
        elif isinstance(block, BSeparator):
            if block.size >= 2:
                state.push_separator()

            state.flush_lines()
        else:
            raise NotImplementedError()

    contents = state.compile()

    if len(contents) == 1:
        return contents[0]

    return CContainer(contents)


def compile_title(state: State, context: Context, title: BTitle):
    heading = CHeading(
        content=compile_block(context, title.content),
        level=title.level,
    )

    state.push(heading)


def compile_list_item(state: State, context: Context, block_item: BListItem):
    last = state.last_content

    if isinstance(last, CFigure):
        last = last.content

    if isinstance(last, CList) and last.ordered == block_item.ordered:
        active_list = last
    else:
        active_list = CList([], block_item.ordered)

        state.push(active_list)

    item_content = compile_block(context, block_item.content)
    item = CListItem(content=item_content)

    active_list.items.append(item)


def compile_table_row(state: State, context: Context, row: BTableRow):
    last = state.last_content

    if isinstance(last, CTable):
        active_table = last
    else:
        active_table = CTable([])

        state.push(active_table)

    cells = [compile_table_cell(context, cell) for cell in row.cells]

    row = CTableRow(cells=cells)

    active_table.rows.append(row)


def compile_table_cell(context: Context, cell: BTableCell) -> CTableCell:
    if isinstance(cell.content, BTitle):
        header = True
        block = cell.content.content
    else:
        header = False
        block = cell.content

    content = compile_block(context, block)

    return CTableCell(content, header)


def compile_pre_caption(state: State, context: Context, element: MarkedBlock):
    state.pending_caption = compile_block(context, element.content)


def compile_post_caption(state: State, context: Context, element: MarkedBlock):
    caption = compile_block(context, element.content)

    last = state.last_content

    if isinstance(last, CTable):
        last.caption = caption
    else:
        content = state.pop()

        figure = CFigure(content, caption)

        state.push(figure)


def compile_code_block(state: State, context: Context, block: BCodeBlock):
    content = CCodeBlock(text=block.text)

    state.push(content)


def compile_directive(state: State, context: Context, directive: BDirective):
    if directive.name == 'include':
        if len(directive.values) != 1:
            raise Exception('Expected one argument')
        content = compile_include(context, directive.values[0])

        if content is not None:
            state.push(content)
    elif directive.name == 'stylesheet':
        if len(directive.values) != 1:
            raise Exception('Expected one argument')
        compile_stylesheet(context, directive.values[0])
    else:
        raise Exception(f'directive not implemented: {directive.name}')


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
