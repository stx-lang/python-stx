from __future__ import annotations
from typing import Set, List, Optional

from stx.reader import Reader, ETX, EOT


class Component:

    def __init__(self):
        self.ids: Set[str] = set()

    def parse(self, reader: Reader):
        raise NotImplementedError()


class TextContent(Component):
    items: List[TextItem]

    def parse(self, reader: Reader):
        self.parse_text(reader, [''])

    def parse_text(self, reader: Reader, stop_marks: List[str]):
        self.items = []

        while not reader.test(EOT):
            if reader.pull(ETX):
                break
            elif reader.test(stop_marks[-1]):
                break
            elif reader.test('-'):
                break
            elif reader.test('*'):
                item = StyledText('*')
            elif reader.test('_'):
                item = StyledText('_')
            elif reader.test('`'):
                item = StyledText('`')
            elif reader.test('['):
                item = LinkText()
            else:
                item = PlainText()

            item.parse_text(reader, stop_marks)

            self.items.append(item)


class TextItem:

    def parse_text(self, reader: Reader, stop_marks: List[str]):
        raise NotImplementedError()


class PlainText(TextItem):
    content: str

    def parse_text(self, reader: Reader, stop_marks: List[str]):
        self.content = ''

        last = None

        while not reader.test(EOT):
            if reader.test(ETX):
                break

            if last == '\n' and reader.any('-'):
                break

            if last != '\\' and reader.test(stop_marks[-1]):
                break

            if last != '\\' and reader.any('*', '_', '`', '['):
                break

            c = reader.read_char()

            self.content += c

            last = c

    def dump(self, data):
        data['content'] = self.content


class StyledText(TextItem):
    content: TextContent

    def __init__(self, delimiter: str):
        super().__init__()
        self.delimiter = delimiter

    def parse_text(self, reader: Reader, stop_marks: List[str]):
        location0 = reader.location

        reader.expect(self.delimiter)

        stop_marks.append(self.delimiter)

        self.content = TextContent()
        self.content.parse_text(reader, stop_marks)

        stop_marks.pop()

        if not reader.pull(self.delimiter):
            raise Exception(
                f'{reader.location}: Expected `{self.delimiter}` started at {location0}.')


class LinkText(TextItem):
    content: TextContent
    reference: str

    def parse_text(self, reader: Reader, stop_marks: List[str]):
        location0 = reader.location

        reader.expect('[')

        stop_marks.append(']')

        self.content = TextContent()
        self.content.parse_text(reader, stop_marks)

        stop_marks.pop()

        if not reader.pull(']'):
            raise Exception(f'{reader.location}: Expected `]` started at {location0}.')

        if reader.pull('('):
            self.reference = ''

            while not reader.test(')'):
                # TODO what about reading a SEP?
                self.reference += reader.read_char()

            reader.expect(')')


class Title(Component):
    level: int
    content: TextContent

    def parse(self, reader: Reader):
        reader.expect('=')

        self.level = 1

        while reader.pull('='):
            self.level += 1

        while reader.pull(' '):
            pass

        reader.push_indent(reader.column)

        self.content = TextContent()
        self.content.parse(reader)

        reader.pop_indent()


class TableCell(Component):
    pass


class TableRow(Component):

    def __init__(self):
        super().__init__()
        self.header = False

    def dump(self, data):
        data['header'] = self.header


class Table(Component):
    pass


class ListItem(Component):
    content: Content

    def __init__(self, ordered: bool):
        super().__init__()
        self.ordered = ordered

    def parse(self, reader: Reader):
        reader.pull('-')

        while reader.pull(' '):
            pass

        reader.push_indent(reader.column)

        self.content = Content()
        self.content.parse(reader)

        reader.pop_indent()


class CodeBlock(Component):
    pass


class Content(Component):
    components: List[Component]

    def parse(self, reader: Reader):
        self.components = []

        while not reader.pull(EOT):
            if reader.test(' '):
                raise Exception(f'{reader.location}: Unexpected whitespace.')
            elif reader.test('='):
                component = Title()
            elif reader.test('-'):
                component = ListItem(ordered=False)
            elif reader.test('.'):
                component = ListItem(ordered=True)
            elif reader.test('|'):
                component = TableRow()
            elif reader.test('`'):
                raise NotImplementedError()
            else:
                component = TextContent()

            component.parse(reader)

            self.components.append(component)


