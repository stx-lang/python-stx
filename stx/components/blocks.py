from typing import List, Optional


class Block:

    pass


class LineText(Block):

    def __init__(self, content: str):
        self.content = content


class Title(Block):

    def __init__(self, content: Block, level: int):
        self.content = content
        self.level = level


class Separator(Block):

    def __init__(self):
        self.size = 1


class TableCell(Block):

    def __init__(self, content: Block):
        self.content = content


class TableRow(Block):

    def __init__(self, cells: List[TableCell]):
        self.cells = cells


class Table(Block):
    pass


class ListItem(Block):

    def __init__(self, content: Block, ordered: bool):
        self.content = content
        self.ordered = ordered


class CodeBlock(Block):

    def __init__(self, content: str):
        self.content = content


class Attribute(Block):

    def __init__(self, name: str, value: Optional[str]):
        self.name = name
        self.value = value


class Content(Block):

    def __init__(self, components: List[Block]):
        self.components = components
