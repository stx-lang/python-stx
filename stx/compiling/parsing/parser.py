from stx.compiling.reading.content import Content
from stx.components import Separator, Component, Composite
from stx.compiling.marks import heading_marks, \
    directive_mark, attribute_mark, code_block_mark, content_box_mark, \
    table_h_row_mark, table_d_row_mark, table_cell_mark, pre_caption_mark, \
    post_caption_mark, ordered_list_item_mark, unordered_list_item_mark, \
    exit_mark
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
            self, indentation: int, breakable=True) -> Component:
        location = self.get_location()

        self.composer.push()

        while self.active():
            content = self.get_content()

            if not content.move_to_indentation(indentation):
                break
            elif content.peek() == self.stop_char:
                break

            # TODO check if it is alive

            location = content.get_location()

            mark = content.read_mark()
            mark_indentation = content.column
            root_indentation = indentation

            if mark is None:
                self.parse_paragraph(location, content)
            elif mark == exit_mark:
                break
            elif mark in heading_marks:
                parent_section = self.get_parent_section()
                section_level = len(mark)

                if (parent_section is not None
                        and parent_section.level >= section_level):
                    content.go_back(location)
                    break
                else:
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
