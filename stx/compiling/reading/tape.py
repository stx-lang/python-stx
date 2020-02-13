from typing import Optional

from stx.utils.stx_error import StxError


class Tape:

    def __init__(self, text: str):
        self.text = text
        self.position = 0
        self.length = len(text)

    def peek(self) -> Optional[str]:
        if self.position >= self.length:
            return None
        return self.text[self.position]

    def move_next(self):
        if self.position >= self.length:
            raise StxError('EOF')
        self.position += 1

    def cut(self, begin: int, end: int):
        # TODO validations
        return self.text[begin:end]
