from typing import List, Optional

from stx.components.content import CContent, CStyledText, CLinkText, \
    CPlainText, CParagraph
from stx.utils import Stack


class Tape:

    def __init__(self, content: str):
        self.content = content
        self.length = len(content)
        self.position = 0

    def read(self) -> str:
        if self.position >= self.length:
            raise Exception()

        c = self.content[self.position]

        self.position += 1

        return c

    def alive(self):
        return self.position < self.length

    def test(self, c: Optional[str]) -> bool:
        if not c:
            return False
        elif self.position >= self.length:
            return False

        return self.content[self.position] == c

    def any(self, *chars: str) -> bool:
        for c in chars:
            if self.test(c):
                return True
        return False

    def pull(self, c: str) -> bool:
        if self.test(c):
            self.read()
            return True

        return False

