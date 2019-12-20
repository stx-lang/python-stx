from typing import Optional


def generate_error_message(message, file_path, line_index, column_index):
    location = ''

    if file_path:
        location += file_path

    if line_index is not None and column_index is not None:
        location += f' @ Line {line_index + 1}, Column {column_index + 1}'
    elif line_index is not None:
        location += f' @ Line {line_index + 1}'
    elif column_index is not None:
        location += f' @ Column {column_index + 1}'

    return f'{location}:\n{message}'


class ParseError(Exception):

    def __init__(
            self,
            message: str,
            file_path: Optional[str] = None,
            line_index: Optional[int] = None,
            column_index: Optional[int] = None):
        super().__init__(generate_error_message(message, file_path, line_index, column_index))

