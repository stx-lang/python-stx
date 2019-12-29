heading6_mark = '======'
heading5_mark = '====='
heading4_mark = '===='
heading3_mark = '==='
heading2_mark = '=='
heading1_mark = '='
unordered_list_item_mark = '-'
ordered_list_item_mark = '.'
table_h_row_mark = '|='
table_d_row_mark = '|-'
table_cell_mark = '|'
pre_caption_mark = '>'
post_caption_mark = '<'
content_box_mark = '!'
code_block_mark = '```'
comment_block_mark = '///'
attribute_mark = '@'
directive_mark = '#'

escape_mark = '\\'

# The order matters for finding the level
heading_marks = [
    heading1_mark,
    heading2_mark,
    heading3_mark,
    heading4_mark,
    heading5_mark,
    heading6_mark,
]

flat_block_marks = [
    code_block_mark,
    comment_block_mark,
]

# The order matters for parsing
reserved_block_marks = [
    heading6_mark,
    heading5_mark,
    heading4_mark,
    heading3_mark,
    heading2_mark,
    heading1_mark,
    unordered_list_item_mark,
    ordered_list_item_mark,
    table_d_row_mark,
    table_h_row_mark,
    table_cell_mark,
    pre_caption_mark,
    post_caption_mark,
    attribute_mark,
    directive_mark,
    code_block_mark,
    content_box_mark,
    comment_block_mark,
]

strong_mark = '*'
emphasis_mark = '_'
code_mark = '`'
begin_link_mark = '['
begin_macro_mark = '<'

reserved_text_marks = [
    strong_mark,
    emphasis_mark,
    code_mark,
    begin_link_mark,
    begin_macro_mark,
]


def get_heading_level(mark):
    if mark not in heading_marks:
        raise Exception(f'`{mark}` is not a heading mark.')
    return heading_marks.index(mark) + 1
