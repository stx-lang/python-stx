

class Location:

    def __init__(self, line: int, column: int, file: str):
        self.line = line
        self.column = column
        self.file = file

    def __repr__(self) -> str:
        return f'{self.file} @ {self.position}'

    @property
    def position(self) -> str:
        return f'Line {self.line + 1}, Column {self.column + 1}'
