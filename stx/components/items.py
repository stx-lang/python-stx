from typing import Optional

from stx.components.base import Item, Component


class StyledText(Item):

    def __init__(self, content: Component, style: str):
        self.content = content
        self.delimiter = style


class LinkText(Item):

    def __init__(self, content: Component, reference: Optional[str]):
        self.content = content
        self.reference = reference

