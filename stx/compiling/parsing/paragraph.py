from abc import ABC
from io import StringIO
from typing import List, Optional

from stx.compiling.reading.content import Content
from stx.compiling.reading.location import Location
from stx.components import PlainText, Component, LinkText, StyledText, \
    Paragraph
from stx.compiling.parsing.abstract import AbstractParser
from stx.utils.stx_error import StxError

# TODO add macros

ESCAPE_CHAR = '\\'

LINK_BEGIN_CHAR = '['
LINK_END_CHAR = ']'
LINK_REF_BEGIN_CHAR = '('
LINK_REF_END_CHAR = ')'

STYLE_CHAR_TOKEN_MAP = {
    '*': 'strong',
    '_': 'emphasized',
    '`': 'code',
}

BEGIN_CHAR_LIST = [LINK_BEGIN_CHAR] + list(STYLE_CHAR_TOKEN_MAP.keys())


class ParaContext:

    def __init__(self, content: Content, indentation: int):
        self.content = content
        self.indentation = indentation
        self.alive = True


class ParagraphParser(AbstractParser, ABC):

    def parse_paragraph(self, location: Location, content: Content) -> bool:
        context = ParaContext(
            content=content,
            indentation=content.column,
        )

        contents = self.parse_contents(context)

        if content.alive(context.indentation):  # TODO this should be implicit
            content.skip_empty_line()

        if len(contents) == 0:
            return False

        self.composer.add(Paragraph(location, contents))
        return True

    def parse_contents(
            self, context: ParaContext) -> List[Component]:
        contents = []

        while context.alive:
            location = context.content.get_location()

            c = context.content.peek()

            if c is None or c == self.stop_char:
                break
            elif c == LINK_BEGIN_CHAR:
                context.content.move_next()

                with self.using_stop_char(LINK_END_CHAR):
                    children = self.parse_contents(context)

                if context.content.peek() != LINK_END_CHAR:
                    raise StxError('Expected link end char')

                context.content.move_next()

                if context.content.peek() == LINK_REF_BEGIN_CHAR:
                    context.content.move_next()

                    with self.using_stop_char(LINK_REF_END_CHAR):
                        ref = self.consume_text(context, greedy=True)

                    if context.content.peek() != LINK_REF_END_CHAR:
                        raise StxError('expected link ref end char')

                    context.content.move_next()
                else:
                    ref = None

                contents.append(
                    LinkText(location, children, ref)
                )
            elif c in STYLE_CHAR_TOKEN_MAP:
                context.content.move_next()

                token = STYLE_CHAR_TOKEN_MAP[c]
                with self.using_stop_char(c):
                    children = self.parse_contents(context)

                if context.content.peek() != c:
                    raise StxError(f'Unclosed style: {token}')

                context.content.move_next()

                contents.append(
                    StyledText(location, children, token)
                )
            else:
                text = self.consume_text(context, greedy=False)

                if text != '':
                    contents.append(
                        PlainText(location, text)
                    )

        return contents

    def consume_text(self, context: ParaContext, greedy: bool) -> str:
        out = StringIO()

        while context.alive:
            c = context.content.peek()

            if c is None or c == self.stop_char or (
                    not greedy and c in BEGIN_CHAR_LIST):
                break
            elif c == '\n':
                if out.getvalue().strip(' ') == '':
                    context.alive = False
                    context.content.move_next()
                    return ''

                out.write(c)
                context.content.move_next()

                with context.content:
                    spaces = context.content.read_spaces(context.indentation)

                    if context.content.peek() is None:
                        context.alive = False
                        context.content.commit()
                        break
                    if context.content.peek() == '\n':
                        context.content.move_next()
                        context.alive = False
                        context.content.commit()
                        break
                    elif spaces < context.indentation:
                        context.alive = False
                        context.content.rollback()
                        break
                    else:
                        context.content.commit()
                        continue
            elif c == ESCAPE_CHAR:
                context.content.move_next()

                c = context.content.peek()

                if c is None:
                    raise StxError('expected special char')
                elif c != self.stop_char and (greedy or c not in BEGIN_CHAR_LIST):
                    raise StxError('invalid escaped char')

            out.write(c)
            context.content.move_next()

        return out.getvalue()
