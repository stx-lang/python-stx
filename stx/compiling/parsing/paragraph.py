from abc import ABC
from io import StringIO
from typing import List, Optional, Tuple

from stx.compiling.reading.content import Content
from stx.compiling.reading.location import Location
from stx.components import PlainText, Component, LinkText, StyledText
from stx.components import Paragraph, MacroText, CapturedText
from stx.compiling.parsing.abstract import AbstractParser
from stx.data_notation.parsing import skip_void, parse_entry
from stx.utils.stx_error import StxError

# TODO add macros

ESCAPE_CHAR = '\\'

LINK_BEGIN_CHAR = '['
LINK_END_CHAR = ']'
LINK_REF_BEGIN_CHAR = '('
LINK_REF_END_CHAR = ')'

CAPTURING_BEGIN_CHAR = '<'
CAPTURING_END_CHAR = '>'
CAP_CLASS_BEGIN_CHAR = '('
CAP_CLASS_END_CHAR = ')'

MACRO_BEGIN_CHAR = '{'
MACRO_END_CHAR = '}'

STYLE_CHAR_TOKEN_MAP = {
    '*': 'strong',
    '_': 'emphasized',
    '`': 'code',
}

BEGIN_CHAR_LIST = [
    LINK_BEGIN_CHAR, CAPTURING_BEGIN_CHAR, MACRO_BEGIN_CHAR
] + list(STYLE_CHAR_TOKEN_MAP.keys())


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
                children, ref = self.read_delimited_contents_and_text(
                    context,
                    LINK_BEGIN_CHAR,
                    LINK_END_CHAR,
                    LINK_REF_BEGIN_CHAR,
                    LINK_REF_END_CHAR,
                )

                contents.append(
                    LinkText(location, children, ref)
                )
            elif c == CAPTURING_BEGIN_CHAR:
                children, cap_class = self.read_delimited_contents_and_text(
                    context,
                    CAPTURING_BEGIN_CHAR,
                    CAPTURING_END_CHAR,
                    CAP_CLASS_BEGIN_CHAR,
                    CAP_CLASS_END_CHAR,
                )

                contents.append(
                    CapturedText(location, children, cap_class)
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
            elif c == MACRO_BEGIN_CHAR:
                context.content.move_next()

                skip_void(context.content)

                entry = parse_entry(context.content)

                skip_void(context.content)

                if context.content.peek() != MACRO_END_CHAR:
                    raise StxError(f'Expected macro end char')

                context.content.move_next()

                contents.append(
                    MacroText(location, entry)
                )
            else:
                text = self.consume_text(context, greedy=False)

                if text != '':
                    contents.append(
                        PlainText(location, text)
                    )

        return contents

    def read_delimited_text(
            self,
            context: ParaContext,
            text_begin: str,
            text_end: str):
        if context.content.peek() != text_begin:
            raise StxError(f'Expected char: {text_begin}')

        context.content.move_next()

        with self.using_stop_char(text_end):
            text = self.consume_text(context, greedy=True)

        if context.content.peek() != text_end:
            raise StxError(f'Expected char: {text_end}')

        context.content.move_next()

        return text

    def read_delimited_contents_and_text(
            self,
            context: ParaContext,
            contents_begin: str,
            contents_end: str,
            text_begin: str,
            text_end: str) -> Tuple[List[Component], Optional[str]]:
        if context.content.peek() != contents_begin:
            raise StxError(f'Expected char: {contents_begin}')

        context.content.move_next()

        with self.using_stop_char(contents_end):
            contents = self.parse_contents(context)

        if context.content.peek() != contents_end:
            raise StxError(f'Expected char: {contents_end}')

        context.content.move_next()

        if context.content.peek() == text_begin:
            text = self.read_delimited_text(context, text_begin, text_end)
        else:
            text = None

        return contents, text

    def consume_text(self, context: ParaContext, greedy: bool) -> str:
        out = StringIO()

        while context.alive:
            c = context.content.peek()

            if c is None or c == self.stop_char or (
                    not greedy and c in BEGIN_CHAR_LIST):
                break
            elif c == '\n':
                out.write(c)
                context.content.move_next()

                if context.content.consume_empty_line():
                    context.alive = False
                    break

                loc0 = context.content.get_location()

                spaces = context.content.read_spaces(context.indentation)

                if spaces < context.indentation:
                    context.alive = False
                    context.content.go_back(loc0)
                    break
                else:
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
