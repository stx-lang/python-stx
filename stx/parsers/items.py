
def parse_styled_text(
        reader: Reader,
        stop_marks: Stack[str]) -> Optional[StyledText]:
    location0 = reader.location

    if reader.pull('*'):
        style = 'bold'
        delimiter = '*'
    else:
        return None

    stop_marks.push(delimiter)

    content = parse_text_content(reader, stop_marks)

    stop_marks.pop()

    if not reader.pull(delimiter):
        raise Exception(
            f'{reader.location}: Expected `{delimiter}` started at {location0}.')

    return StyledText(content, style)


def parse_link_text(reader, stop_marks: Stack[str]) -> Optional[LinkText]:
    location0 = reader.location

    if not reader.pull('['):
        return None

    stop_marks.push(']')

    content = parse_text_content(reader, stop_marks)

    stop_marks.pop()

    if not reader.pull(']'):
        raise Exception(f'{reader.location}: Expected `]` started at {location0}.')

    if reader.pull('('):
        reference = ''

        while not reader.test(')'):
            # TODO what about reading a SEP?
            reference += reader.read_char()

        reader.expect(')')
    else:
        reference = None

    return LinkText(content, reference)

