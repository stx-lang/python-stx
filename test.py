from stx import json
from stx.parsers.blocks import parse_content
from stx.reader import Reader
from stx.utils import Stack


def main():
    pass


class Abc:

    def __init__(self, x):
        self.x = x


if __name__ == '__main__':
    with open("example/book.txt", "r", encoding="utf-8") as f:
        content = f.read()
        reader = Reader(content)

        document = parse_content(reader, Stack())

        print(json.dumps(document, indent=2))
