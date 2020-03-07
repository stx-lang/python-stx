import string
from io import StringIO
from typing import Optional, List, Union

from stx.compiling.reading.content import Content
from stx.data_notation.values import Value, Token, Entry, Group, Empty
from stx.utils.stx_error import StxError

TOKEN_DELIMITER_CHAR = '`'
TOKEN_CHARS = string.ascii_letters + string.digits + '_-./'
TOKEN_ESCAPE_CHAR = '\\'
ENTRY_SEPARATOR_CHAR = ':'
GROUP_SEPARATOR_CHAR = ','
GROUP_BEGIN_CHAR = '('
GROUP_END_CHAR = ')'
EMPTY_CHAR = '~'
WHITESPACE_CHARS = ' \t\r\n'


def parse_value(content: Content) -> Value:
    values = parse_values(content)
    length = len(values)

    if length == 0:
        return Empty()
    elif length == 1:
        return values[0]
    return Group(values)


def parse_entry(content: Content) -> Entry:
    location = content.get_location()

    entry = try_parse_entry(content)

    if entry is None:
        raise StxError('Expected token or entry', location)

    return entry


def try_parse_entry(content: Content) -> Optional[Entry]:
    token_or_entry = try_parse_token_or_entry(content)

    if token_or_entry is None:
        return None

    return token_or_entry.to_entry()


def parse_values(content: Content) -> List[Value]:
    items = []

    can_be_none = True

    while True:
        loc0 = content.get_location()

        value = try_parse_item(content)

        if value is None:
            if can_be_none:
                content.go_back(loc0)
                break
            else:
                raise Exception('Expected to read a group item')

        items.append(value)

        loc0 = content.get_location()

        skip_void(content)

        c = content.peek()

        if c == GROUP_SEPARATOR_CHAR:
            content.move_next()

            skip_void(content)

            can_be_none = False
        else:
            content.go_back(loc0)
            break

    return items


def try_parse_item(
        content: Content,
        allow_entry_separator=True) -> Optional[Value]:
    c = content.peek()

    if c == EMPTY_CHAR:
        content.move_next()

        return Empty()

    group = try_parse_group(content)

    if group is not None:
        return group

    return try_parse_token_or_entry(content, allow_entry_separator)


def try_parse_group(content: Content):
    c = content.peek()

    if c == GROUP_BEGIN_CHAR:
        content.move_next()

        skip_void(content)

        items = parse_values(content)

        skip_void(content)

        c = content.peek()

        if c != GROUP_END_CHAR:
            raise StxError('Expected group end char', content.get_location())

        content.move_next()

        return Group(items)

    return None


def try_parse_token_or_entry(
        content: Content,
        allow_entry_separator=True) -> Union[Token, Entry, None]:
    text = try_parse_text(content)

    if text is None:
        return None

    loc0 = content.get_location()

    skip_void(content)

    c = content.peek()

    if c == ENTRY_SEPARATOR_CHAR and allow_entry_separator:
        content.move_next()

        skip_void(content)

        entry_name = text
        entry_value = try_parse_item(content, allow_entry_separator=False)

        if entry_value is None:
            raise StxError('Expected an entry value', content.get_location())

        return Entry(entry_name, entry_value)

    group = try_parse_group(content)

    if group is not None:
        return Entry(text, group)

    # go before skipping void
    content.go_back(loc0)

    return Token(text)


def try_parse_text(content: Content) -> Optional[str]:
    c = content.peek()

    if c in TOKEN_CHARS:
        out = StringIO()

        while True:
            out.write(c)

            content.move_next()

            c = content.peek()

            if c is None or c not in TOKEN_CHARS:
                break

        return out.getvalue()
    elif c == TOKEN_DELIMITER_CHAR:
        content.move_next()

        out = StringIO()

        while True:
            c = content.peek()

            if c is None:
                raise Exception(f'Expected {TOKEN_DELIMITER_CHAR}')
            elif c == TOKEN_DELIMITER_CHAR:
                content.move_next()
                break
            elif c == TOKEN_ESCAPE_CHAR:
                content.move_next()

                c = content.peek()

                if c is None:
                    raise Exception('Expected escaped char.')
                elif c in [TOKEN_ESCAPE_CHAR, TOKEN_DELIMITER_CHAR]:
                    out.write(c)

                    content.move_next()
                else:
                    # TODO add unicode support

                    raise Exception(f'Invalid escaped char: {c}')
            else:
                content.move_next()

                out.write(c)

        return out.getvalue()

    return None


def skip_void(content: Content):
    while True:
        c = content.peek()

        if c is None:
            break
        elif c in WHITESPACE_CHARS:
            content.move_next()
        else:
            break
