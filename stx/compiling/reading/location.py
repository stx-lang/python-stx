

class Location:

    def __init__(self, file_path: str, line: int, column: int, position: int):
        self.file_path = file_path
        self.line = line
        self.column = column
        self.position = position

    def __str__(self):
        return (f'{self.file_path} @'
                f' Line {self.line + 1},'
                f' Column {self.column + 1}')

    def decorate(self, message: str):
        return f'{message} << {self}'
