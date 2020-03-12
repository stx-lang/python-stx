from io import StringIO
from typing import List, Optional

from stx.compiling.composer import Composer

from stx.compiling.marks import heading_block_marks, header_row_block_mark, \
    not_inline_marks, inline_marks, link_ref_begin_mark, link_ref_end_mark
from stx.compiling.marks import normal_row_block_mark, cell_block_mark
from stx.compiling.marks import pre_caption_block_mark
from stx.compiling.marks import post_caption_block_mark
from stx.compiling.marks import unordered_item_block_mark
from stx.compiling.marks import ordered_item_block_mark, section_levels
from stx.compiling.marks import link_text_begin_mark, link_text_end_mark
from stx.compiling.marks import container_begin_mark, container_end_mark
from stx.compiling.marks import function_begin_mark, function_end_mark
from stx.compiling.marks import attribute_special_mark, directive_special_mark
from stx.compiling.marks import all_marks, escape_char, literal_area_mark
from stx.compiling.marks import container_area_begin_mark
from stx.compiling.marks import container_area_end_mark
from stx.compiling.marks import strong_begin_mark, strong_end_mark
from stx.compiling.marks import emphasized_begin_mark, emphasized_end_mark
from stx.compiling.marks import code_begin_mark, code_end_mark
from stx.compiling.marks import deleted_begin_mark, deleted_end_mark
from stx.compiling.marks import d_quote_begin_mark, d_quote_end_mark
from stx.compiling.marks import s_quote_begin_mark, s_quote_end_mark
from stx.compiling.marks import ellipsis_single_mark

from stx.compiling.reading.content import Content
from stx.compiling.reading.location import Location
from stx.compiling.reading.reader import Reader

from stx.components import Component, Section, Composite, Table, TableRow, \
    Paragraph, DisplayMode
from stx.components import LinkText, StyledText, PlainText, Literal, ListBlock
from stx.components import TableOfContents, FunctionCall

from stx.data_notation.parsing import parse_entry, skip_void, try_parse_entry
from stx.data_notation.values import Value

from stx.document import Document
from stx.outputs import make_output_action

from stx.utils.closeable import Closeable
from stx.utils.debug import see
from stx.utils.files import resolve_include_files
from stx.utils.stx_error import StxError

PASS = 0
EXIT = 1
CONSUMED = 2


class CTX:

    def __init__(self, document: Document, reader: Reader):
        self.reader = reader
        self.document = document
        self.composer = Composer()
        self.stop_mark_stack = []
        self.section_stack: List[Section] = []

    def get_parent_section(self) -> Optional[Section]:
        if len(self.section_stack) > 0:
            return self.section_stack[-1]
        return None

    @property
    def stop_mark(self) -> Optional[str]:  # TODO rename to stop token
        if len(self.stop_mark_stack) == 0:
            return None
        return self.stop_mark_stack[-1]

    def using_stop_mark(self, char: str) -> Closeable:
        def enter_action():
            self.stop_mark_stack.append(char)

        def exit_action():
            self.stop_mark_stack.pop()

        return Closeable(enter_action, exit_action)


def capture(ctx: CTX):
    ctx.document.content = capture_component(
        ctx,
        indentation=0,
        breakable=False)

    if ctx.reader.active():
        raise StxError('Unexpected content.', ctx.reader.get_location())

    # TODO improve error messages
    if len(ctx.composer.stack) > 0:
        raise StxError('unclosed components')
    elif not ctx.composer.attributes_buffer.empty():
        raise StxError(
            f'not consumed attributes: {ctx.composer.attributes_buffer}')
    elif len(ctx.composer.pre_captions) > 0:
        raise StxError(
            'not consumed pre captions: ',
            ctx.composer.pre_captions[0].location)


def capture_component(
        ctx: CTX,
        indentation: int,
        breakable=True) -> Component:
    location = ctx.reader.get_location()

    ctx.composer.push()

    while ctx.reader.active():
        content = ctx.reader.get_content()

        while content.consume_empty_line():
            pass

        if not content.consume_indentation(indentation):
            break
        elif content.test(ctx.stop_mark):
            break
        elif content.peek() is None:
            break

        location = content.get_location()

        mark = content.read_mark(not_inline_marks)

        signal = (
                parse_section(ctx, mark, location, content, indentation)
                or
                parse_list(ctx, mark, location, content)
                or
                parse_table(ctx, mark, location, content)
                or
                parse_caption(ctx, mark, content)
                or
                parse_literal(ctx, mark, location, content, indentation)
                or
                parse_container(ctx, mark, location, content, indentation)
                or
                parse_attribute(ctx, mark, content)
                or
                parse_directive(ctx, mark, location)
        )

        if signal == PASS:
            parse_inline_component(ctx, mark, location, content, indentation)
        elif signal == CONSUMED:
            pass
        elif signal == EXIT:
            break
        else:
            raise AssertionError(f'Illegal signal: {signal}')

    components = ctx.composer.pop()

    if len(components) == 0:
        # TODO Blank component
        return Composite(location, [])
    elif len(components) == 1:
        return components[0]

    return Composite(location, components)


def parse_section(
        ctx: CTX,
        mark: str,
        location: Location,
        content: Content,
        before_mark_indentation: int) -> int:
    if mark not in heading_block_marks:
        return PASS

    parent_section = ctx.get_parent_section()
    section_level = section_levels[mark]

    if (parent_section is not None
            and parent_section.level >= section_level):
        content.go_back(location)
        return EXIT

    # TODO is this ok?
    skip_void(content)

    after_mark_indentation = content.column

    section = Section(location, section_level)

    ctx.composer.add(section)

    ctx.section_stack.append(section)

    section.heading = capture_component(ctx, after_mark_indentation, True)
    section.content = capture_component(ctx, before_mark_indentation, True)

    ctx.section_stack.pop()

    return CONSUMED


def parse_list(
        ctx: CTX,
        mark: str,
        location: Location,
        content: Content) -> int:
    if mark == ordered_item_block_mark:
        ordered = True
    elif mark == unordered_item_block_mark:
        ordered = False
    else:
        return PASS

    list_block = ctx.composer.get_last_component()

    if not isinstance(list_block, ListBlock):
        list_block = ListBlock(location, ordered)

        ctx.composer.add(list_block)

    # TODO is this ok?
    skip_void(content)

    indentation = content.column

    list_item = capture_component(ctx, indentation, True)

    list_block.items.append(list_item)

    return CONSUMED


def parse_table(
        ctx: CTX,
        mark: str,
        location: Location,
        content: Content) -> int:
    if mark == header_row_block_mark:
        header = True
        reuse_row = False
    elif mark == normal_row_block_mark:
        header = False
        reuse_row = False
    elif mark == cell_block_mark:
        header = False
        reuse_row = True
    else:
        return PASS

    table = ctx.composer.get_last_component()

    if not isinstance(table, Table):
        table = Table(location)

        ctx.composer.add(table)

    row = table.get_last_row() if reuse_row else None

    if row is None:
        row = TableRow(location, header)

        table.rows.append(row)

    # TODO is this ok?
    skip_void(content)

    indentation0 = content.column
    indentation = indentation0

    while True:
        with ctx.using_stop_mark(cell_block_mark):
            cell = capture_component(ctx, indentation, True)

            row.cells.append(cell)

        if not ctx.reader.active():
            break

        content = ctx.reader.get_content()

        loc0 = content.get_location()

        # Consume indentation when it is the beginning of the line
        if content.column == 0:
            if content.read_spaces(indentation0) < indentation0:
                content.go_back(loc0)
                break

        if content.peek() == cell_block_mark:
            content.move_next()
            content.read_spaces()

            indentation = content.column
        else:
            break

    return CONSUMED


def parse_caption(ctx: CTX, mark: str, content: Content) -> int:
    if mark == pre_caption_block_mark:
        pre_mode = True
    elif mark == post_caption_block_mark:
        pre_mode = False
    else:
        return PASS

    # TODO is this ok?
    skip_void(content)

    caption = capture_component(ctx, content.column, True)

    if pre_mode:
        ctx.composer.push_pre_caption(caption)
    else:
        ctx.composer.push_post_caption(caption)

    return CONSUMED


def parse_literal(
        ctx: CTX, mark: str, location: Location, content: Content,
        indentation_before_mark: int) -> int:
    if mark != literal_area_mark:
        return PASS

    content.read_spaces()

    function_location = content.get_location()

    function = try_parse_entry(content)

    content.expect_end_of_line()

    out = StringIO()

    while True:
        line = content.read_line(indentation_before_mark)

        if line is None:
            raise StxError(f'Expected: {mark}', content.get_location())
        elif line.startswith(escape_char):
            line = line[1:]  # remove escape char

            if not line.startswith(mark) and not line.startswith(escape_char):
                raise StxError(f'Invalid escaped sequence, expected:'
                               f' {see(mark)} or {see(escape_char)}.')
        elif line.rstrip() == mark:
            break

        out.write(line)

    text = out.getvalue()

    if function is not None:
        component = FunctionCall(
            function_location,
            inline=False,
            key=function.name,
            options=function.value,
            argument=Literal(location, text),
        )
    else:
        component = Literal(location, text)

    ctx.composer.add(component)

    return CONSUMED


def parse_container(
        ctx: CTX, mark: str, location: Location, content: Content,
        indentation_before_mark: int) -> int:
    if mark != container_area_begin_mark:
        return PASS

    content.read_spaces()

    function = try_parse_entry(content)

    content.expect_end_of_line()

    with ctx.using_stop_mark(container_area_end_mark):
        component = capture_component(ctx, indentation_before_mark)

    content.pull(container_area_end_mark)
    content.expect_end_of_line()

    if function is not None:
        component = FunctionCall(
            location,
            inline=False,
            key=function.name,
            options=function.value,
            argument=component,
        )

    ctx.composer.add(component)

    return CONSUMED


def parse_attribute(ctx: CTX, mark: str, content: Content) -> int:
    if mark != attribute_special_mark:
        return PASS

    entry = parse_entry(content)

    content.expect_end_of_line()

    ctx.composer.push_attribute(entry.name, entry.value)

    return CONSUMED


def parse_directive(ctx: CTX, mark: str, location: Location) -> int:
    if mark != directive_special_mark:
        return PASS

    content = ctx.reader.get_content()
    file_path = content.file_path

    entry = parse_entry(content)

    key = entry.name
    value = entry.value

    if content.column > 0:
        content.expect_end_of_line()

    if key == 'title':
        ctx.document.title = value.to_str()
    elif key == 'author':
        ctx.document.author = value.to_str()
    elif key == 'format':
        ctx.document.format = value.to_str()
    elif key == 'encoding':
        ctx.document.encoding = value.to_str()
    elif key == 'stylesheets':
        ctx.document.stylesheets = value.to_list()
    elif key == 'include':
        process_import(ctx, location, file_path, value)
    elif key == 'output':
        process_output(ctx, location, value)
    else:
        raise StxError(f'Unsupported directive: {key}')

    return CONSUMED


def process_import(
        ctx: CTX,
        location: Location,
        file_path: str,
        include_path: Value):
    file_paths = resolve_include_files(include_path.to_str(), file_path)

    ctx.reader.push_files(file_paths)


def process_output(ctx: CTX, location: Location, value: Value):
    action = make_output_action(ctx.document, location, value)

    ctx.document.actions.append(action)


def parse_inline_component(
        ctx: CTX,
        mark: str,
        location: Location,
        content: Content,
        indentation: int):
    inlines = parse_inline(ctx, location, content, indentation)

    if len(inlines) == 0:
        # TODO return empty component
        raise StxError('Missing content.', location)
    elif len(inlines) == 1 and inlines[0].display_mode == DisplayMode.BLOCK:
        component = inlines[0]
    else:
        display_mode = DisplayMode.compute_display_mode(inlines)

        if display_mode == DisplayMode.BLOCK:
            component = Composite(location, inlines)
        else:
            component = Paragraph(location, inlines)

    ctx.composer.add(component)


def parse_inline(
        ctx: CTX, location: Location,
        content: Content, indentation: int) -> List[Component]:
    ctx.composer.push()

    try:
        while not content.halted():
            if content.test(ctx.stop_mark):
                break

            location = content.get_location()

            mark = content.read_mark(inline_marks)

            signal = (
                parse_inline_function(ctx, mark, location, content)
                or
                parse_inline_container(ctx, mark, location, content, indentation)
                or
                parse_inline_style(ctx, mark, location, content, indentation)
                or
                parse_inline_link(ctx, mark, location, content, indentation)
                or
                parse_inline_token(ctx, mark, location, content, indentation)
                or
                parse_inline_text(ctx, mark, location, content, indentation)
            )

            if signal == PASS:
                raise StxError(f'Not implemented mark: {mark}')
            elif signal == CONSUMED:
                pass
            elif signal == EXIT:
                break
            else:
                raise AssertionError(f'Illegal signal: {signal}')
    except StxError as e:
        raise StxError('Error parsing inline content.', location) from e

    return ctx.composer.pop()


def parse_inline_function(
        ctx: CTX, mark: str, location: Location, content: Content) -> int:
    if mark != function_begin_mark:
        return PASS

    skip_void(content)

    function_location = content.get_location()

    function = parse_entry(content)

    skip_void(content)

    if not content.pull(function_end_mark):
        raise StxError(f'Expected mark: {function_end_mark}')

    ctx.composer.add(
        FunctionCall(
            function_location,
            inline=True,
            key=function.name,
            options=function.value))

    return CONSUMED


def parse_inline_container(
        ctx: CTX, mark: str, location: Location,
        content: Content, indentation: int) -> int:
    if mark != container_begin_mark:
        return PASS

    with ctx.using_stop_mark(container_end_mark):
        # It uses the original indentation
        #   so the paragraph can be continued.
        contents = parse_inline(
            ctx, content.get_location(), content, indentation)

    if not content.pull(container_end_mark):
        raise StxError(f'Expected mark: {container_end_mark}')

    if not content.pull(function_begin_mark):
        raise StxError(f'Expected mark: {function_begin_mark}')

    skip_void(content)

    function_location = content.get_location()

    function = parse_entry(content)

    skip_void(content)

    if not content.pull(function_end_mark):
        raise StxError(f'Expected mark: {function_end_mark}')

    ctx.composer.add(
        FunctionCall(
            function_location,
            inline=True,
            key=function.name,
            options=function.value,
            argument=Composite(location, contents)))

    return CONSUMED


def parse_inline_style(
        ctx: CTX, mark: str, location: Location,
        content: Content, indentation: int) -> int:
    if mark == strong_begin_mark:
        end_mark = strong_end_mark
        style = 'strong'
    elif mark == emphasized_begin_mark:
        end_mark = emphasized_end_mark
        style = 'emphasized'
    elif mark == code_begin_mark:
        end_mark = code_end_mark
        style = 'code'
    elif mark == deleted_begin_mark:
        end_mark = deleted_end_mark
        style = 'deleted'
    elif mark == d_quote_begin_mark:
        end_mark = d_quote_end_mark
        style = 'double-quote'
    elif mark == s_quote_begin_mark:
        end_mark = s_quote_end_mark
        style = 'single-quote'
    else:
        return PASS

    with ctx.using_stop_mark(end_mark):
        # It uses the original indentation
        #   so the paragraph can be continued.
        contents = parse_inline(
            ctx, content.get_location(), content, indentation)

    if not content.pull(end_mark):
        raise StxError(f'Expected mark: {end_mark}')

    ctx.composer.add(
        StyledText(location, contents, style)
    )

    return CONSUMED


def parse_inline_link(
        ctx: CTX, mark: str, location: Location,
        content: Content, indentation: int) -> int:
    if mark != link_text_begin_mark:
        return PASS

    with ctx.using_stop_mark(link_text_end_mark):
        # It uses the original indentation
        #   so the paragraph can be continued.
        contents = parse_inline(
            ctx, content.get_location(), content, indentation)

    if not content.pull(link_text_end_mark):
        raise StxError(f'Expected mark: {link_text_end_mark}')

    if content.pull(link_ref_begin_mark):
        out = StringIO()

        while not content.pull(link_ref_end_mark):
            c = content.peek()

            if c is None:
                raise StxError(
                    f'Expected {link_ref_end_mark}', content.get_location())

            out.write(c)
            content.move_next()

        reference = out.getvalue()
    else:
        reference = None

    ctx.composer.add(LinkText(location, contents, reference))

    return CONSUMED


def parse_inline_token(
        ctx: CTX, mark: str, location: Location,
        content: Content, indentation: int) -> int:
    if mark == ellipsis_single_mark:
        text = '\u2026'
    else:
        return PASS

    ctx.composer.add(
        PlainText(location, text)
    )

    return CONSUMED


def parse_inline_text(
        ctx: CTX, mark: str, location: Location,
        content: Content, indentation: int) -> int:
    if mark is not None:
        return PASS

    out = StringIO()

    completed = False

    while content.peek() is not None:
        # Check if the text is broken by an inline or stop mark
        if content.test_any(inline_marks):
            break
        elif content.test(ctx.stop_mark):
            break

        c = content.peek()

        if c == '\n':
            out.write(c)
            content.move_next()

            # Check if the text is completed by an empty line
            if content.consume_empty_line():
                completed = True
                break

            loc0 = content.get_location()

            spaces = content.read_spaces(indentation)

            # Check if the text is completed by indentation change
            if spaces < indentation:
                content.go_back(loc0)
                completed = True
                break

            # Check if the text is completed by a non-inline mark
            if content.test_any(not_inline_marks):
                content.go_back(loc0)
                completed = True
                break
        elif c == escape_char:
            content.move_next()

            escaped_mark = content.pull_any(all_marks)
            if escaped_mark is not None:
                out.write(escaped_mark)
            elif content.pull(ctx.stop_mark):
                out.write(ctx.stop_mark)
            elif content.pull(escape_char):
                out.write(escape_char)
            else:
                raise StxError('invalid escaped char')
        else:
            out.write(c)
            content.move_next()

    text = out.getvalue()

    if text == '':
        return EXIT

    ctx.composer.add(
        PlainText(location, text)
    )

    if completed:
        return EXIT
    return CONSUMED
