import string
from io import StringIO
from typing import Any, Union, Optional, Tuple

from stx.parsing3.source import Source
from stx.utils.stx_error import StxError

STRING_DELIMITER_CHARS = ['\"', '\'']  # TODO change to string instead of list
LIST_BEGIN_CHAR = '['
LIST_END_CHAR = ']'
DICT_BEGIN_CHAR = '{'
DICT_END_CHAR = '}'
SEPARATOR_CHAR = ','
NAME_BEGIN_CHARS = string.ascii_letters
NAME_OTHER_CHARS = string.ascii_letters + string.digits + '_-'


def skip_whitespace(source):
    source.read_while([' ', '\n', '\r', '\t'])


def parse_value(source: Source) -> Any:
    c = source.peek()

    if c in STRING_DELIMITER_CHARS:
        return parse_string(source)
    elif c == LIST_BEGIN_CHAR:
        return parse_list(source)
    elif c == DICT_BEGIN_CHAR:
        return parse_dict(source)
    elif c in string.digits:
        return parse_number(source)
    elif c in NAME_BEGIN_CHARS:
        return parse_name(source)
    else:
        raise StxError(f'Unexpected character: {c}')


def parse_string(source: Source) -> str:
    delimiter = source.expect_char(STRING_DELIMITER_CHARS)

    out = StringIO()

    while True:
        c = source.read_next()

        if c is None:
            raise StxError('Expected to read a string character.')
        elif c == '\\':
            c = source.read_next()

            if c in ['\'', '\"', '\\', '/']:
                out.write(c)
            elif c == 'b':
                out.write('\b')
            elif c == 'f':
                out.write('\f')
            elif c == 'n':
                out.write('\n')
            elif c == 'r':
                out.write('\r')
            elif c == 't':
                out.write('\t')
            elif c == 'u':
                hex_digits = source.read_max(4)

                if len(hex_digits) != 4:
                    raise StxError('Expected 4 hex digits.')

                unicode = int(hex_digits, 16)

                out.write(chr(unicode))
        elif c == delimiter:
            break

        out.write(c)

    return out.getvalue()


def parse_list(source: Source) -> list:
    source.expect_char([LIST_BEGIN_CHAR])

    skip_whitespace(source)

    c = source.peek()

    if c == LIST_END_CHAR:
        source.move_next()
        return []

    items = []

    while True:
        item = parse_value(source)

        items.append(item)

        skip_whitespace(source)

        c = source.peek()

        if c == SEPARATOR_CHAR:
            source.move_next()

            skip_whitespace(source)
            continue
        elif c == LIST_END_CHAR:
            source.move_next()
            break
        else:
            raise StxError(f'Unexpected character: {c}')

    return items


def parse_entry(source: Source) -> Tuple[Any, Any]:
    key = parse_value(source)

    skip_whitespace(source)

    c = source.peek()

    if c == ':':
        source.move_next()

        skip_whitespace(source)

        value = parse_value(source)
    else:
        value = None

    return key, value


def parse_dict(source: Source) -> dict:
    source.expect_char([DICT_BEGIN_CHAR])

    skip_whitespace(source)

    c = source.peek()

    if c == DICT_END_CHAR:
        source.move_next()
        return {}

    result = {}

    while True:
        key, value = parse_entry(source)

        result[key] = value

        skip_whitespace(source)

        c = source.peek()

        if c == SEPARATOR_CHAR:
            source.move_next()

            skip_whitespace(source)
            continue
        elif c == DICT_END_CHAR:
            source.move_next()
            break
        else:
            raise StxError(f'Unexpected character: {c}')

    return result


def parse_number(source: Source) -> Union[float, int]:
    raise NotImplementedError()


def parse_name(source: Source) -> str:
    out = StringIO()

    c = source.read_next()

    if c is None or c not in NAME_BEGIN_CHARS:
        raise StxError('Expected name begin char.')

    out.write(c)

    while True:
        c = source.peek()

        if c is None or c not in NAME_OTHER_CHARS:
            break

        out.write(c)
        source.move_next()

    return out.getvalue()
