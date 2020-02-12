from io import StringIO
from typing import Any

DEFAULT_MAX_LENGTH = 40


def quote_string(value: str, max_length: int) -> str:
    out = StringIO()

    out.write('`')

    actual_length = 0

    for c in value:
        if actual_length >= max_length:
            break
        elif c == '\\':
            out.write('\\\\')
        elif c == '\n':
            out.write('\\n')
        elif c == '\r':
            out.write('\\r')
        elif c == '\t':
            out.write('\\t')
        else:
            unicode = ord(c)

            if 0x20 <= unicode <= 0x7E:
                out.write(c)
            else:
                out.write(f'\\({unicode})')

        actual_length += 1

    if actual_length < len(value):
        out.write('\u2026')

    out.write('`')

    return out.getvalue()


def see(value: Any) -> str:
    if isinstance(value, str):
        return quote_string(str(value), DEFAULT_MAX_LENGTH)
    elif isinstance(value, int):
        return str(value)

    return f'{type(value).__name__}<{hash(value)}>'
