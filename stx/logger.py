import sys

from stx.compiling.reading.location import Location


def debug(message: str, location: Location = None):
    print(message if location is None else location.decorate(message))


def info(message: str, location: Location = None):
    print(message if location is None else location.decorate(message))


def warning(message: str, location: Location = None):
    print(
        message if location is None else location.decorate(message),
        file=sys.stderr)
