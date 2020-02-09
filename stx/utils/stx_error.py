from stx.utils.thread_context import context


def generate_error_message(message):
    source = context.source

    return (
        f'{source.file_path}@{source._line + 1},{source._column + 1}:\n'
        f'  {message}'
    )


class StxError(Exception):

    def __init__(self, message: str):
        super().__init__(generate_error_message(message))