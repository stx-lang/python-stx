from typing import List, Dict, Optional

# Block marks

heading6_block_mark = '======'  # TODO rename to section
heading5_block_mark = '====='
heading4_block_mark = '===='
heading3_block_mark = '==='
heading2_block_mark = '=='
heading1_block_mark = '='
unordered_item_block_mark = '-'
ordered_item_block_mark = '.'
header_row_block_mark = '|='
normal_row_block_mark = '|-'
cell_block_mark = '|'
pre_caption_block_mark = '::'
post_caption_block_mark = ':^'

# Wrapping marks

function_begin_mark = '<'
function_end_mark = '>'
container_begin_mark = '{'
container_end_mark = '}'
strong_begin_mark = '*'
strong_end_mark = '*'
emphasized_begin_mark = '_'
emphasized_end_mark = '_'
code_begin_mark = '`'
code_end_mark = '`'
deleted_begin_mark = '~~'
deleted_end_mark = '~~'
d_quote_begin_mark = '""'
d_quote_end_mark = '""'
s_quote_begin_mark = '\'\''
s_quote_end_mark = '\'\''
link_text_begin_mark = '['
link_text_end_mark = ']'
link_ref_begin_mark = '('
link_ref_end_mark = ')'

# Single Marks

ellipsis_single_mark = '...'

# Area marks

literal_area_mark = '+++'
container_area_begin_mark = '{{{'
container_area_end_mark = '}}}'

# Special Marks

attribute_special_mark = '@'
directive_special_mark = '#'
exit_special_mark = '%'

escape_char = '\\'


# Summaries (the order matters for parsing)

heading_block_marks = [
    heading6_block_mark,
    heading5_block_mark,
    heading4_block_mark,
    heading3_block_mark,
    heading2_block_mark,
    heading1_block_mark,
]

section_levels = {
    heading1_block_mark: 1,
    heading2_block_mark: 2,
    heading3_block_mark: 3,
    heading4_block_mark: 4,
    heading5_block_mark: 5,
    heading6_block_mark: 6,
}

style_token_map = {
    '*': 'strong',
    '_': 'emphasized',
    '`': 'code',
}


def get_matching_mark(text: str, valid_marks: List[str]) -> Optional[str]:
    for mark in valid_marks:
        if text.startswith(mark):
            return mark

    return None


not_inline_marks = [
    heading6_block_mark,
    heading5_block_mark,
    heading4_block_mark,
    heading3_block_mark,
    heading2_block_mark,
    heading1_block_mark,

    unordered_item_block_mark,
    ordered_item_block_mark,
    header_row_block_mark,
    normal_row_block_mark,
    cell_block_mark,
    pre_caption_block_mark,
    post_caption_block_mark,

    literal_area_mark,
    container_area_begin_mark,
    container_area_end_mark,

    attribute_special_mark,
    directive_special_mark,
    exit_special_mark,
]


inline_marks = [
    function_begin_mark,
    container_begin_mark,
    strong_begin_mark,
    emphasized_begin_mark,
    code_begin_mark,
    deleted_begin_mark,
    d_quote_begin_mark,
    s_quote_begin_mark,
    link_text_begin_mark,
    ellipsis_single_mark,
]

all_marks = not_inline_marks + inline_marks

mark_max_length = max(len(mark) for mark in all_marks)
