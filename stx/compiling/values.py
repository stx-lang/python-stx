import string
from io import StringIO
from typing import Any, Union, Optional, Tuple

from stx.compiling.reading.content import Content

from stx.utils.stx_error import StxError

STRING_DELIMITER_CHARS = ['\"', '\'']  # TODO change to string instead of list
LIST_BEGIN_CHAR = '['
LIST_END_CHAR = ']'
DICT_BEGIN_CHAR = '{'
DICT_END_CHAR = '}'
SEPARATOR_CHAR = ','
NAME_BEGIN_CHARS = string.ascii_letters
NAME_OTHER_CHARS = string.ascii_letters + string.digits + '_-'


def skip_whitespace(content):
    content.read_while([' ', '\n', '\r', '\t'])


def parse_value(content: Content) -> Any:
    c = content.peek()

    if c in STRING_DELIMITER_CHARS:
        return parse_string(content)
    elif c == LIST_BEGIN_CHAR:
        return parse_list(content)
    elif c == DICT_BEGIN_CHAR:
        return parse_dict(content)
    elif c in string.digits:
        return parse_number(content)
    elif c in NAME_BEGIN_CHARS:
        return parse_name(content)
    else:
        raise StxError(f'Unexpected character: {c}')


def parse_string(content: Content) -> str:
    delimiter = content.expect_char(STRING_DELIMITER_CHARS)

    out = StringIO()

    while True:
        c = content.read_next()

        if c is None:
            raise StxError('Expected to read a string character.')
        elif c == '\\':
            c = content.read_next()

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
                hex_digits = content.read_max(4)

                if len(hex_digits) != 4:
                    raise StxError('Expected 4 hex digits.')

                unicode = int(hex_digits, 16)

                out.write(chr(unicode))
        elif c == delimiter:
            break

        out.write(c)

    return out.getvalue()


def parse_list(content: Content) -> list:
    content.expect_char([LIST_BEGIN_CHAR])

    skip_whitespace(content)

    c = content.peek()

    if c == LIST_END_CHAR:
        content.move_next()
        return []

    items = []

    while True:
        item = parse_value(content)

        items.append(item)

        skip_whitespace(content)

        c = content.peek()

        if c == SEPARATOR_CHAR:
            content.move_next()

            skip_whitespace(content)
            continue
        elif c == LIST_END_CHAR:
            content.move_next()
            break
        else:
            raise StxError(f'Unexpected character: {c}')

    return items


def parse_entry(content: Content) -> Tuple[Any, Any]:
    key = parse_value(content)

    skip_whitespace(content)

    c = content.peek()

    if c == ':':
        content.move_next()

        skip_whitespace(content)

        value = parse_value(content)
    else:
        value = None

    return key, value


def parse_dict(content: Content) -> dict:
    content.expect_char([DICT_BEGIN_CHAR])

    skip_whitespace(content)

    c = content.peek()

    if c == DICT_END_CHAR:
        content.move_next()
        return {}

    result = {}

    while True:
        key, value = parse_entry(content)

        result[key] = value

        skip_whitespace(content)

        c = content.peek()

        if c == SEPARATOR_CHAR:
            content.move_next()

            skip_whitespace(content)
            continue
        elif c == DICT_END_CHAR:
            content.move_next()
            break
        else:
            raise StxError(f'Unexpected character: {c}')

    return result


def parse_number(content: Content) -> Union[float, int]:
    raise NotImplementedError()


def parse_name(content: Content) -> str:
    out = StringIO()

    c = content.read_next()

    if c is None or c not in NAME_BEGIN_CHARS:
        raise StxError('Expected name begin char.')

    out.write(c)

    while True:
        c = content.peek()

        if c is None or c not in NAME_OTHER_CHARS:
            break

        out.write(c)
        content.move_next()

    return out.getvalue()
