from stx.utils.thread_context import context


def generate_error_message(message):
    reader = context.reader

    if reader is None:
        return message

    content = reader.get_content()

    return (
        f'{content.file_path}@{content.line + 1},{content.column + 1}:\n'
        f'  {message}'
    )


class StxError(Exception):

    def __init__(self, message: str):
        super().__init__(generate_error_message(message))