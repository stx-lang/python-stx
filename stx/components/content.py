from __future__ import annotations

import re
from typing import Optional, List, Iterable

from stx.attributes_map import AttributesMap


class CContent:
    _attributes = None

    @property
    def attributes(self) -> AttributesMap:
        if self._attributes is None:
            self._attributes = AttributesMap()
        return self._attributes

    def get_plain_text(self) -> List[str]:
        raise NotImplementedError()

    def get_children(self) -> List[CContent]:
        raise NotImplementedError()

    def walk(self) -> Iterable[CContent]:
        for content in self.get_children():
            yield content

            for item in content.walk():
                yield item


def get_plain_text_of_contents(contents: List[CContent]):
    items = []

    for content in contents:
        items += content.get_plain_text()

    return items


class CStyledText(CContent):

    def __init__(self, contents: List[CContent], style: str):
        self.contents = contents
        self.style = style

    def get_plain_text(self) -> List[str]:
        return get_plain_text_of_contents(self.contents)

    def get_children(self) -> List[CContent]:
        return self.contents

    def __repr__(self):
        return f'StyledText[{self.style}|{"|".join(str(self.contents))}]'


class CLinkText(CContent):

    def __init__(self, contents: List[CContent], reference: Optional[str]):
        self.contents = contents
        self.reference = reference

    @property
    def internal(self) -> bool:
        # TODO refactor to external
        return self.reference is not None and not re.match(r'(?i)^([a-z]+:)?//', self.reference)

    def get_plain_text(self) -> List[str]:
        return get_plain_text_of_contents(self.contents)

    def get_children(self) -> List[CContent]:
        return self.contents

    def __repr__(self):
        return f'LinkText[{self.reference}|{"|".join(str(self.contents))}]'


class CPlainText(CContent):

    def __init__(self, text: str):
        self.text = text

    def get_plain_text(self) -> List[str]:
        return [self.text]

    def get_children(self) -> List[CContent]:
        return []

    def __repr__(self):
        return f'PlainText[{self.text}]'


class CRawText(CContent):

    def __init__(self, lines: List[str]):
        self.lines = lines

    def get_plain_text(self) -> List[str]:
        return self.lines

    def get_children(self) -> List[CContent]:
        return []

    def __repr__(self):
        return f'RawText[{len(self.lines)} lines]'


class CParagraph(CContent):

    def __init__(self, contents: List[CContent]):
        self.contents = contents

    def get_plain_text(self) -> List[str]:
        return get_plain_text_of_contents(self.contents)

    def get_children(self) -> List[CContent]:
        return self.contents

    def __repr__(self):
        return f'Paragraph[{self.get_plain_text()}'


class CListItem(CContent):

    def __init__(self, content: CContent):
        self.content = content

    def get_plain_text(self) -> List[str]:
        return self.content.get_plain_text()

    def get_children(self) -> List[CContent]:
        return [self.content]


class CList(CContent):

    def __init__(self, items: List[CListItem], ordered: bool):
        self.items = items
        self.ordered = ordered

    def get_plain_text(self) -> List[str]:
        return get_plain_text_of_contents(self.items)

    def get_children(self) -> List[CContent]:
        return self.items


class CTableCell(CContent):

    def __init__(self, content: CContent, header: bool):
        self.content = content
        self.header = header

    def get_plain_text(self) -> List[str]:
        return self.content.get_plain_text()

    def get_children(self) -> List[CContent]:
        return [self.content]


class CTableRow(CContent):

    def __init__(self, cells: List[CTableCell]):
        self.cells = cells

    @property
    def header(self) -> bool:
        for cell in self.cells:
            if cell.header:
                return True
        return False

    def get_plain_text(self) -> List[str]:
        return get_plain_text_of_contents(self.cells)

    def get_children(self) -> List[CContent]:
        return self.cells


class CTable(CContent):

    def __init__(self, rows: List[CTableRow]):
        self.rows = rows
        self.caption = None
        self.number = None

    def get_plain_text(self) -> List[str]:
        return get_plain_text_of_contents(self.get_children())

    def get_children(self) -> List[CContent]:
        return self.rows


class CFigure(CContent):

    def __init__(self, content: CContent, caption: CContent):
        self.content = content
        self.caption = caption
        self.number = None

    def get_plain_text(self) -> List[str]:
        return get_plain_text_of_contents(self.get_children())

    def get_children(self) -> List[CContent]:
        return [self.content, self.caption]


class CHeading(CContent):

    def __init__(self, content: CContent, level: int):
        self.content = content
        self.level = level
        self.number: Optional[str] = None

    def get_plain_text(self) -> List[str]:
        return self.content.get_plain_text()

    def get_children(self) -> List[CContent]:
        return [self.content]

    def __repr__(self):
        return f'H{self.level}[{self.content}]'


class CCodeBlock(CContent):

    def __init__(self, text: str):
        self.text = text

    def get_plain_text(self) -> List[str]:
        return [self.text]

    def get_children(self) -> List[CContent]:
        return []


class CEmbeddedText(CContent):

    def __init__(self, text: str, source: str):
        self.text = text
        self.source = source

    def get_plain_text(self) -> List[str]:
        return []

    def get_children(self) -> List[CContent]:
        return []


class CContainer(CContent):

    def __init__(self, contents: List[CContent]):
        self.contents = contents

    def get_plain_text(self) -> List[str]:
        return get_plain_text_of_contents(self.contents)

    def get_children(self) -> List[CContent]:
        return self.contents
