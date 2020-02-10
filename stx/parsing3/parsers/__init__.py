from stx.components import Separator
from stx.parsing3.marks import heading_marks, get_section_level, \
    directive_mark, attribute_mark, code_block_mark, content_box_mark, \
    table_h_row_mark, table_d_row_mark, table_cell_mark, pre_caption_mark, \
    post_caption_mark, ordered_list_item_mark, unordered_list_item_mark
from stx.parsing3.parsers.attribute import AttributeParser
from stx.parsing3.parsers.base import BaseParser
from stx.parsing3.parsers.caption import CaptionParser
from stx.parsing3.parsers.code_block import CodeBlockParser
from stx.parsing3.parsers.content_box import ContentBoxParser
from stx.parsing3.parsers.directive import DirectiveParser
from stx.parsing3.parsers.list_block import ListBlockParser
from stx.parsing3.parsers.paragraph import ParagraphParser
from stx.parsing3.parsers.section import SectionParser
from stx.parsing3.parsers.table import TableParser
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
    BaseParser,
):

    def parse_components(
            self,
            indentation: int,
            breakable=True):
        while self.source.alive(indentation):
            self.source.checkout_position()

            mark = self.source.read_mark()

            if mark is None:
                self.source.commit_position()
                text = self.source.read_text(indentation=self.source.column)

                if len(text) > 0:
                    self.parse_paragraph(text)
                elif breakable:
                    break  # TODO
                else:
                    self.composer.add(Separator())
            else:
                mark_indentation = self.source.column
                root_indentation = indentation

                if mark in heading_marks:
                    section_level = get_section_level(mark)
                    parent_section = self.section_stack[-1] if len(self.section_stack) > 0 else None

                    if parent_section is not None and parent_section.level >= section_level:
                        self.source.rollback_position()
                        break
                    else:
                        self.source.commit_position()

                    self.parse_section(
                        section_level,
                        mark_indentation, root_indentation)
                else:
                    self.source.commit_position()

                    if mark == directive_mark:
                        self.parse_directive()
                    elif mark == attribute_mark:
                        self.parse_attribute()
                    elif mark == code_block_mark:
                        self.parse_code_block(root_indentation)
                    elif mark == content_box_mark:
                        self.parse_content_box(mark_indentation)
                    elif mark == table_h_row_mark:
                        self.parse_table_row(
                            mark_indentation, header=True)
                    elif mark == table_d_row_mark:
                        self.parse_table_row(
                            mark_indentation, header=True)
                    elif mark == table_cell_mark:
                        self.parse_table_cell(mark_indentation)
                    elif mark == pre_caption_mark:
                        self.parse_pre_caption(mark_indentation)
                    elif mark == post_caption_mark:
                        self.parse_post_caption(mark_indentation)
                    elif mark == unordered_list_item_mark:
                        self.parse_list_item(mark_indentation, False)
                    elif mark == ordered_list_item_mark:
                        self.parse_list_item(mark_indentation, True)
                    else:
                        raise StxError(f'Unsupported mark: `{mark}`')
