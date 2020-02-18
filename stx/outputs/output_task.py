from __future__ import annotations

from typing import Optional

from stx.compiling.reading.location import Location


class OutputTask:

    def __init__(self, location: Location, config: dict):
        self.location = location
        self.options: dict = dict(config)

    @property
    def format(self) -> str:
        return self.options['format']

    @property
    def file(self) -> str:
        return self.options['file']

    @property
    def pretty(self) -> bool:
        if 'pretty' in self.options:
            # TODO parse boolean values
            return self.options['pretty'] in ['True', 'true', '1']
        return False
