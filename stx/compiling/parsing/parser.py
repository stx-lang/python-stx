from stx.compiling.reading.content import Content
from stx.components import Separator, Component, Composite
from stx.compiling.marks import heading_marks, get_section_level, \
    directive_mark, attribute_mark, code_block_mark, content_box_mark, \
    table_h_row_mark, table_d_row_mark, table_cell_mark, pre_caption_mark, \
    post_caption_mark, ordered_list_item_mark, unordered_list_item_mark
from stx.compiling.parsing.attribute import AttributeParser
from stx.compiling.parsing.abstract import AbstractParser
from stx.compiling.parsing.caption import CaptionParser
from stx.compiling.parsing.code_block import CodeBlockParser
from stx.compiling.parsing.content_box import ContentBoxParser
from stx.compiling.parsing.directive import DirectiveParser
from stx.compiling.parsing.list_block import ListBlockParser
from stx.compiling.parsing.paragraph import ParagraphParser
from stx.compiling.parsing.section import SectionParser
from stx.compiling.parsing.table import TableParser
from stx.utils.stx_error import StxError


class Parser(
    AttributeParser,
    CaptionParser,
    CodeBlockParser,
    ContentBoxParser,
    DirectiveParser,
    ListBlockParser,
    ParagraphParser,
    SectionParser,
    TableParser,
    AbstractParser,
):

    def capture(self):
        self.document.content = self.capture_component(
            indentation=0,
            breakable=False)

        # TODO improve error messages
        if len(self.composer.stack) > 0:
            raise StxError('unclosed components')
        elif len(self.composer.attributes_buffer) > 0:
            raise StxError(
                f'not consumed attributes: {self.composer.attributes_buffer}')
        elif len(self.composer.pre_captions) > 0:
            raise StxError(
                'not consumed pre captions: ',
                self.composer.pre_captions[0].location)

    def capture_component(
            self,
            indentation: int,
            breakable=True) -> Component:
        location = self.get_location()

        self.composer.push()

        while self.active():
            content = self.get_content()

            if not content.alive(indentation):
                break
            elif content.peek() == self.stop_char:
                break

            with content:
                location = content.get_location()
                mark = content.read_mark(self.stop_char)  # TODO is stop char still required?

                if mark is None:
                    content.commit()

                    if self.parse_paragraph(location, content):
                        continue
                    elif breakable:
                        break  # TODO

                    self.composer.add(Separator(location))
                    continue
                elif mark in heading_marks:
                    section_level = get_section_level(mark)
                    parent_section = (
                        self.section_stack[-1]
                        if len(self.section_stack) > 0 else None
                    )

                    if (parent_section is not None
                            and parent_section.level >= section_level):
                        content.rollback()
                        break

                    content.commit()
                    parse_section = True
                else:
                    content.commit()
                    parse_section = False

            mark_indentation = content.column
            root_indentation = indentation

            if parse_section:
                self.parse_section(
                    location, section_level,
                    mark_indentation, root_indentation)
            elif mark == directive_mark:
                self.parse_directive(location)
            elif mark == attribute_mark:
                self.parse_attribute(location)
            elif mark == code_block_mark:
                self.parse_code_block(location, root_indentation)
            elif mark == content_box_mark:
                self.parse_content_box(location, mark_indentation)
            elif mark == table_h_row_mark:
                self.parse_table_row(
                    location, mark_indentation, header=True)
            elif mark == table_d_row_mark:
                self.parse_table_row(
                    location, mark_indentation, header=False)
            elif mark == table_cell_mark:
                self.parse_table_cell(location, mark_indentation)
            elif mark == pre_caption_mark:
                self.parse_pre_caption(location, mark_indentation)
            elif mark == post_caption_mark:
                self.parse_post_caption(location, mark_indentation)
            elif mark == unordered_list_item_mark:
                self.parse_list_item(
                    location, mark_indentation, ordered=False)
            elif mark == ordered_list_item_mark:
                self.parse_list_item(
                    location, mark_indentation, ordered=True)
            else:
                raise StxError(f'Unsupported mark: `{mark}`')

        component = self.composer.pop()

        if component is None:
            # TODO implement empty component
            return Composite(location)

        return component