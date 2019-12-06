from stx import json
from stx.components import Content
from stx.reader import Reader


def main():
    pass


class Abc:

    def __init__(self, x):
        self.x = x


if __name__ == '__main__':
    with open("example/book.txt", "r", encoding="utf-8") as f:
        content = f.read()
        reader = Reader(content)

        document = Content()
        document.parse(reader)

        print(json.dumps(document, indent=2))
