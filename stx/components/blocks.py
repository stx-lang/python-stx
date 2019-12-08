from typing import List, Optional


class Block:

    pass


class BLineText(Block):

    def __init__(self, text: str):
        self.text = text


class BTitle(Block):

    def __init__(self, content: Block, level: int):
        self.content = content
        self.level = level


class BSeparator(Block):

    def __init__(self):
        self.size = 1


class BTableCell(Block):

    def __init__(self, content: Block):
        self.content = content


class BTableRow(Block):

    def __init__(self, cells: List[BTableCell]):
        self.cells = cells


class BListItem(Block):

    def __init__(self, content: Block, ordered: bool):
        self.content = content
        self.ordered = ordered


class BCodeBlock(Block):

    def __init__(self, text: str):
        self.text = text


class BAttribute(Block):

    def __init__(self, name: str, value: Optional[str]):
        self.name = name
        self.value = value


class BComposite(Block):

    def __init__(self, blocks: List[Block]):
        self.blocks = blocks
