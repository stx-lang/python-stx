from typing import Optional

from stx.components import Component, Composite, CodeBlock, Table, \
    ListBlock, TextBlock, PlainText, StyledText, LinkText, RawText, Figure, \
    Section, Placeholder, Separator, ContentBox
from stx.design.document import Document
from stx.utils.stx_error import StxError


def composite_to_json(composite: Composite) -> dict:
    return {
        'type': 'composite',
        'components': [
            component_to_json(component)
            for component in composite.components
        ],
    }


def code_block_to_json(code_block: CodeBlock) -> dict:
    return {
        'type': 'code-block',
        'lang': code_block.lang,
        'content': code_block.content,
    }


def table_to_json(table: Table) -> dict:
    return {
        'type': 'table',
        'caption': component_to_json(table.caption),
        'number': table.number,
        'rows': [
            {
                'header': row.header,
                'cells': [
                    component_to_json(cell)
                    for cell in row.cells
                ],
            }
            for row in table.rows
        ]
    }


def list_to_json(list_block: ListBlock) -> dict:
    return {
        'type': 'list',
        'ordered': list_block.ordered,
        'items': [
            component_to_json(item)
            for item in list_block.items
        ]
    }


def paragraph_to_json(paragraph: TextBlock) -> dict:
    return {
        'type': 'paragraph',
        'components': [
            component_to_json(component)
            for component in paragraph.components
        ],
    }


def plain_text_to_json(plain_text: PlainText) -> dict:
    return {
        'type': 'plain-text',
        'content': plain_text.content,
    }


def styled_text_to_json(styled_text: StyledText) -> dict:
    return {
        'type': 'styled-text',
        'style': styled_text.style,
        'contents': [
            component_to_json(content)
            for content in styled_text.contents
        ],
    }


def link_text_to_json(link_text: LinkText) -> dict:
    return {
        'type': 'link-text',
        'reference': link_text.reference,
        'contents': [
            component_to_json(content)
            for content in link_text.contents
        ],
    }


def embedded_block_to_json(embedded_block: RawText) -> dict:
    return {
        'type': 'embedded-block',
        # TODO add origin?
        'content': embedded_block.content,
    }


def figure_to_json(figure: Figure) -> dict:
    return {
        'type': 'figure',
        'number': figure.number,
        'content': component_to_json(figure.content),
        'caption': component_to_json(figure.caption),
    }


def section_to_json(section: Section) -> dict:
    return {
        'type': 'section',
        'level': section.level,
        'heading': component_to_json(section.heading),
        'content': component_to_json(section.content),
    }


def placeholder_to_json(placeholder: Placeholder) -> dict:
    return {
        'type': 'placeholder',
        'name': placeholder.name,
    }


def separator_to_json(separator: Separator) -> dict:
    return {
        'type': 'separator',
        'name': separator.level,
    }


def box_to_json(box: ContentBox) -> dict:
    return {
        'type': 'box',
        'style': box.style,
        'content': component_to_json(box.content),
    }


def component_to_json(content: Optional[Component]) -> Optional[dict]:
    if content is None:
        return None
    elif isinstance(content, Composite):
        return composite_to_json(content)
    elif isinstance(content, CodeBlock):
        return code_block_to_json(content)
    elif isinstance(content, Table):
        return table_to_json(content)
    elif isinstance(content, ListBlock):
        return list_to_json(content)
    elif isinstance(content, TextBlock):
        return paragraph_to_json(content)
    elif isinstance(content, PlainText):
        return plain_text_to_json(content)
    elif isinstance(content, StyledText):
        return styled_text_to_json(content)
    elif isinstance(content, LinkText):
        return link_text_to_json(content)
    elif isinstance(content, RawText):
        return embedded_block_to_json(content)
    elif isinstance(content, Figure):
        return figure_to_json(content)
    elif isinstance(content, Section):
        return section_to_json(content)
    elif isinstance(content, Placeholder):
        return placeholder_to_json(content)
    elif isinstance(content, Separator):
        return separator_to_json(content)
    elif isinstance(content, ContentBox):
        return box_to_json(content)
    else:
        raise NotImplementedError(f'Not implemented type: {type(content)}')


def document_to_json(doc: Document) -> dict:
    return {
        'title': doc.title,
        'author': doc.author,
        'content': component_to_json(doc.content)
    }