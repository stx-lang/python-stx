from typing import Optional, List


class CContent:
    _attributes = None

    @property
    def attributes(self) -> dict:
        if self._attributes is None:
            self._attributes = {}
        return self._attributes

    @attributes.setter
    def attributes(self, value: Optional[dict]):
        self._attributes = value


class CStyledText(CContent):

    def __init__(self, content: CContent, style: str):
        self.content = content
        self.style = style


class CLinkText(CContent):

    def __init__(self, content: CContent, reference: Optional[str]):
        self.content = content
        self.reference = reference


class CPlainText(CContent):

    def __init__(self, text: str):
        self.text = text


class CRawText(CContent):

    def __init__(self, lines: List[str]):
        self.lines = lines


class CParagraph(CContent):

    def __init__(self, contents: List[CContent]):
        self.contents = contents


class CListItem(CContent):

    def __init__(self, content: CContent):
        self.content = content


class CList(CContent):

    def __init__(self, items: List[CListItem], ordered: bool):
        self.items = items
        self.ordered = ordered


class CTableCell(CContent):

    def __init__(self, content: CContent, header: bool):
        self.content = content
        self.header = header


class CTableRow(CContent):

    def __init__(self, cells: List[CTableCell]):
        self.cells = cells

    @property
    def header(self) -> bool:
        for cell in self.cells:
            if cell.header:
                return True
        return False


class CTable(CContent):

    def __init__(self, rows: List[CTableRow]):
        self.rows = rows


class CHeading(CContent):

    def __init__(self, content: CContent, level: int):
        self.content = content
        self.level = level


class CCodeBlock(CContent):

    def __init__(self, text: str):
        self.text = text


class CContainer(CContent):

    def __init__(self, contents: List[CContent]):
        self.contents = contents
