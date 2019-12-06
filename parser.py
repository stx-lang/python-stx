from typing import Optional
from stx.components import Document, Component, Title, PlainText, StyledText, Link, \
    ListItem, Paragraph, TableRow, TableCell, Table
from tape import Tape


def parse_document(tape: Tape) -> Document:
    document = Document()

    parse_components(document, tape)

    return document


def parse_components(
        parent: Component, tape: Tape, stop_mark: Optional[str] = None):
    indent = tape.column

    while tape.alive:
        if tape.test('\n'):
            tape.pull()

            if tape.test('\n'):
                raise Exception(f'{tape.location}: Too much space')

        if tape.test(indent * ' '):
            tape.pull(count=indent)
        elif tape.column < indent:
            break

        component = parse_component(tape, stop_mark)

        if component is None:
            break

        parent.contents.append(component)


def parse_component(
        tape: Tape, stop_mark: Optional[str] = None) -> Optional[Component]:
    if not tape.alive:
        return None

    if tape.test(stop_mark):
        if stop_mark == '|' and (tape.test('|=') or tape.test('|-')):
            pass
        else:
            return None

    if tape.test('!!!\n'):
        parse_ignore_block(tape)

    if tape.test('='):
        return parse_title(tape)
    elif tape.test('.'):
        return parse_list_item(tape, ordered=True)
    elif tape.test('-'):
        return parse_list_item(tape, ordered=False)
    elif tape.test('|='):
        return parse_table(tape, header=True)
    elif tape.test('|-'):
        return parse_table(tape, header=False)
    else:
        return parse_paragraph(tape, stop_mark=stop_mark)


def parse_ignore_block(tape: Tape):
    tape.pull(expected='!!!\n')

    while not tape.test('!!!\n'):
        tape.pull()

    tape.pull(expected='!!!\n')

    if tape.test('\n'):
        tape.pull()


def parse_title(tape: Tape) -> Title:
    tape.pull('=')

    level = 1

    while tape.alive and tape.test('='):
        tape.pull()
        level += 1

    while tape.test(' '):
        tape.pull()

    title = Title(level)

    paragraph = parse_paragraph(tape)

    title.contents.append(paragraph)

    return title


def parse_list_item(tape: Tape, ordered: bool) -> ListItem:
    if ordered:
        tape.pull('.')
    else:
        tape.pull('-')

    while tape.test(' '):
        tape.pull()

    list_item = ListItem(ordered)

    parse_components(list_item, tape)

    return list_item


def parse_table(tape: Tape, header: bool) -> Table:
    table = Table()

    table_alive = True

    while table_alive:
        # TODO validate indent
        if header:
            tape.pull('|=')
        else:
            tape.pull('|-')

        while tape.test(' '):
            tape.pull()

        table_row = TableRow(header)

        while True:
            table_cell = TableCell()

            parse_components(table_cell, tape, stop_mark='|')

            table_row.contents.append(table_cell)

            if tape.test('|=') or tape.test('|-'):
                break
            elif tape.test('|'):
                tape.pull()

                if tape.test('--'):
                    tape.pull(count=2)
                    table_alive = False
                    break
                else:
                    while tape.test(' '):
                        tape.pull()
            else:
                break

        table.contents.append(table_row)

    return table


def parse_paragraph(tape: Tape, stop_mark: Optional[str] = None) -> Paragraph:
    buffer = []

    indent = tape.column

    def flush_string() -> str:
        content = ''.join(buffer)
        buffer.clear()
        return content

    stack_comp = [Paragraph()]

    def flush_text():
        content = flush_string()
        if content:
            component = stack_comp[-1]
            component.contents.append(PlainText(content))

    def pop_comp() -> Component:
        component = stack_comp.pop()
        parent = stack_comp[-1]
        parent.contents.append(component)
        return component

    stack_mark = []

    while tape.alive:
        broken = tape.previous == '\n'
        escaped = tape.previous == '\\'

        if stop_mark and tape.test(stop_mark) and not escaped:
            break

        c = tape.pull()

        if c == '\n':
            buffer.append('\n')

            # if it is an empty line, the paragraph is complete
            if broken or (tape.alive and tape.test('\n')):
                break

            # otherwise, it should be indented
            if indent > 0:
                if tape.test(indent * ' '):
                    tape.pull(count=indent)
                else:
                    break
        elif len(stack_mark) > 0 and c == stack_mark[-1] and not escaped:
            stack_mark.pop()

            if c == ']':
                flush_text()

                if tape.test('('):
                    tape.pull()
                    stack_mark.append(')')
                else:
                    pop_comp()
            elif c == ')':
                link = pop_comp()

                if isinstance(link, Link):
                    link.ref = flush_string()
                else:
                    raise Exception('expected a link')
            elif c in ['*', '_', '`'] and not escaped:
                flush_text()

                pop_comp()
            else:
                raise Exception('invalid state')
        elif c == '*' and not escaped:
            flush_text()
            stack_comp.append(StyledText('bold'))
            stack_mark.append('*')
        elif c == '_' and not escaped:
            flush_text()
            stack_comp.append(StyledText('italic'))
            stack_mark.append('_')
        elif c == '`' and not escaped:
            flush_text()
            stack_comp.append(StyledText('code'))
            stack_mark.append('`')
        elif c == '[' and not escaped:
            flush_text()
            stack_comp.append(Link(None))
            stack_mark.append(']')
        else:
            buffer.append(c)

    flush_text()

    # TODO check stacks, should be empty

    return stack_comp.pop()
