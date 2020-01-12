from __future__ import annotations

import re
from io import StringIO
from typing import List, Iterable, Optional, TextIO

from stx.design.attributes_map import AttributesMap

from stx.utils.strs import crop_text


class Component:
    _attributes = None

    @property
    def attributes(self) -> AttributesMap:
        if self._attributes is None:
            self._attributes = AttributesMap()
        return self._attributes

    def get_text(self) -> str:
        output = StringIO()

        self.write_text(output)

        return output.getvalue()

    def walk(self) -> Iterable[Component]:
        for child in self.get_children():
            yield child

            for c in child.walk():
                yield c

    def write_text(self, output: TextIO):
        raise NotImplementedError()

    def get_children(self) -> List[Component]:
        raise NotImplementedError()

    def __repr__(self):
        raise NotImplementedError()


class Composite(Component):

    def __init__(self, components: List[Component]):
        self.components = components

    def __repr__(self):
        return f'Composite<{len(self.components)} component(s)>'

    def write_text(self, output: TextIO):
        for component in self.components:
            component.write_text(output)

    def get_children(self) -> List[Component]:
        return self.components


class Heading(Component):

    def __init__(self, content: Component, level: int):
        self.content = content
        self.level = level
        self.number = None

    def __repr__(self):
        return f'Heading<{crop_text(self.get_text(), 10)}>'

    def write_text(self, output: TextIO):
        self.content.write_text(output)

    def get_children(self) -> List[Component]:
        return [self.content]


class RawText(Component):

    def __init__(self, text: str):
        self.text = text

    def __repr__(self):
        return f'RawText<{crop_text(self.text, 10)}>'

    def write_text(self, output: TextIO):
        output.write(self.text)

    def get_children(self) -> List[Component]:
        return []


class CodeBlock(Component):

    def __init__(self, code: str, flavor: str):
        self.code = code
        self.flavor = flavor

    def __repr__(self):
        return f'CodeBlock<{crop_text(self.code, 10)}>'

    def write_text(self, output: TextIO):
        output.write(self.code)

    def get_children(self) -> List[Component]:
        return []


class TableRow(Component):

    def __init__(self, cells: List[Component], header: bool):
        self.cells = cells
        self.header = header

    def __repr__(self):
        return f'TableRow<{len(self.cells)} cell(s)>'

    def write_text(self, output: TextIO):
        for cell in self.cells:
            cell.write_text(output)

    def get_children(self) -> List[Component]:
        return self.cells


class Table(Component):

    def __init__(self, rows: List[TableRow]):
        self.rows = rows
        self.caption = None
        self.number = None

    def __repr__(self):
        return f'Table<{len(self.rows)} row(s)>'

    def write_text(self, output: TextIO):
        for row in self.rows:
            row.write_text(output)

    def get_children(self) -> List[Component]:
        if self.caption is not None:
            return [self.caption, *self.rows]

        return self.rows


class Figure(Component):

    def __init__(self, content: Component, caption: Component):
        self.content = content
        self.caption = caption
        self.number = None

    def __repr__(self):
        return f'Figure<{crop_text(self.caption.get_text(), 10)}>'

    def write_text(self, output: TextIO):
        self.caption.write_text(output)
        self.content.write_text(output)

    def get_children(self) -> List[Component]:
        return [self.caption, self.content]


class ListBlock(Component):

    def __init__(self, items: List[Component], ordered: bool):
        self.items = items
        self.ordered = ordered

    def __repr__(self):
        return f'ListBlock<{len(self.items)} item(s)>'

    def write_text(self, output: TextIO):
        for item in self.items:
            item.write_text(output)

    def get_children(self) -> List[Component]:
        return self.items


class StyledText(Component):

    def __init__(self, contents: List[Component], style: str):
        self.contents = contents
        self.style = style

    def __repr__(self):
        return f'StyledText<{crop_text(self.get_text(), 10)}>'

    def write_text(self, output: TextIO):
        for content in self.contents:
            content.write_text(output)

    def get_children(self) -> List[Component]:
        return self.contents


class LinkText(Component):

    def __init__(self, contents: List[Component], reference: Optional[str]):
        self.contents = contents
        self.reference = reference

    def __repr__(self):
        return f'LinkText<{crop_text(self.get_text(), 10)}>'

    def write_text(self, output: TextIO):
        for content in self.contents:
            content.write_text(output)

    def get_children(self) -> List[Component]:
        return self.contents

    @property
    def internal(self) -> bool:
        # TODO refactor to external
        return self.reference is not None and not re.match(r'(?i)^([a-z]+:)?//', self.reference)


class PlainText(Component):

    def __init__(self, text: str):
        self.text = text

    def __repr__(self):
        return f'PlainText<{crop_text(self.text, 10)}>'

    def write_text(self, output: TextIO):
        output.write(self.text)

    def get_children(self) -> List[Component]:
        return []


class TextBlock(Component):

    def __init__(self, components: List[Component]):
        self.components = components

    def __repr__(self):
        return f'TextBlock<{crop_text(self.get_text(), 10)}>'

    def write_text(self, output: TextIO):
        for component in self.components:
            component.write_text(output)

    def get_children(self) -> List[Component]:
        return self.components


class Placeholder(Component):

    def __init__(self, name: str):
        self.name = name

    def write_text(self, output: TextIO):
        pass

    def get_children(self) -> List[Component]:
        return []

    def __repr__(self):
        return f'Placeholder<{self.name}>'


class Section(Component):

    def __init__(self, heading: Heading, components: List[Component]):
        self.heading = heading
        self.components = components

    def __repr__(self):
        return f'Section<{len(self.components)} component(s)>'

    def write_text(self, output: TextIO):
        self.heading.write_text(output)

        for component in self.components:
            component.write_text(output)

    def get_children(self) -> List[Component]:
        return [self.heading, *self.components]
