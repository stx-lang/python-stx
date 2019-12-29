from typing import Optional

from stx.parsing._location import Location


class ParseError(Exception):

    def __init__(self, message: str, location: Location):
        super().__init__(f'{location}:\n{message}')
