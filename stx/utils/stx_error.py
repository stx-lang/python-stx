from typing import Optional

from stx.compiling.reading.location import Location
from stx.utils.thread_context import context


def generate_error_message(message: str, location: Optional[Location]):
    if location is None:
        reader = context.parser

        if reader is not None:
            content = reader.get_content()
            location = content.get_location()

    if location is None:
        return message

    return location.decorate(message)


class StxError(Exception):

    # TODO make location required
    def __init__(self, message: str, location: Location = None):
        super().__init__(generate_error_message(message, location))
