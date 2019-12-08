from __future__ import annotations
from typing import Optional, List


class CContent:
    _attributes = None
    _ids = None

    @property
    def attributes(self) -> dict:
        if self._attributes is None:
            self._attributes = {}
        return self._attributes

    @attributes.setter
    def attributes(self, value: Optional[dict]):
        self._attributes = value

    @property
    def ids(self) -> List[str]:
        if self._ids is None:
            self._ids = list()

        return self._ids

    def get_plain_text(self) -> List[str]:
        raise NotImplementedError()

    def get_children(self) -> List[CContent]:
        raise NotImplementedError()


class WithCaption:
    caption: Optional[CContent]


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


class CLinkText(CContent):

    def __init__(self, contents: List[CContent], reference: Optional[str]):
        self.contents = contents
        self.reference = reference

    def get_plain_text(self) -> List[str]:
        return get_plain_text_of_contents(self.contents)

    def get_children(self) -> List[CContent]:
        return self.contents


class CPlainText(CContent):

    def __init__(self, text: str):
        self.text = text

    def get_plain_text(self) -> List[str]:
        return [self.text]

    def get_children(self) -> List[CContent]:
        return []


class CRawText(CContent):

    def __init__(self, lines: List[str]):
        self.lines = lines

    def get_plain_text(self) -> List[str]:
        return self.lines

    def get_children(self) -> List[CContent]:
        return []


class CParagraph(CContent):

    def __init__(self, contents: List[CContent]):
        self.contents = contents

    def get_plain_text(self) -> List[str]:
        return get_plain_text_of_contents(self.contents)

    def get_children(self) -> List[CContent]:
        return self.contents


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


class CTable(CContent, WithCaption):

    def __init__(
            self, rows: List[CTableRow], caption: Optional[CContent] = None):
        self.rows = rows
        self.caption = caption

    def get_plain_text(self) -> List[str]:
        return get_plain_text_of_contents(self.get_children())

    def get_children(self) -> List[CContent]:
        children = list(self.rows)

        if self.caption is not None:
            children += [self.caption]

        return children


class CHeading(CContent):

    def __init__(self, content: CContent, level: int):
        self.content = content
        self.level = level

    def get_plain_text(self) -> List[str]:
        return self.content.get_plain_text()

    def get_children(self) -> List[CContent]:
        return [self.content]


class CCodeBlock(CContent, WithCaption):

    def __init__(self, text: str, caption: Optional[CContent] = None):
        self.text = text
        self.caption = caption

    def get_plain_text(self) -> List[str]:
        items = [self.text]

        if self.caption is not None:
            items += self.caption.get_plain_text()

        return items

    def get_children(self) -> List[CContent]:
        if self.caption is not None:
            return [self.caption]

        return []


class CContainer(CContent):

    def __init__(self, contents: List[CContent]):
        self.contents = contents

    def get_plain_text(self) -> List[str]:
        return get_plain_text_of_contents(self.contents)

    def get_children(self) -> List[CContent]:
        return self.contents