from typing import Optional, List

from stx.compiling.reading.location import Location
from stx.components import Component, Composite, CodeBlock, Table, Image, \
    FunctionCall, CustomText
from stx.components import ListBlock, Paragraph, PlainText, StyledText
from stx.components import LinkText, Literal, Figure, Section, Separator
from stx.components import ContentBox, TableOfContents, ElementReference
from stx.components import CapturedText
from stx.document import Document
from stx.utils.stx_error import StxError


def location_to_json(location: Optional[Location]) -> Optional[dict]:
    if location is None:
        return None

    return {
        'file_path': location.file_path,
        'line': location.line,
        'column': location.column,
    }


def extend_base(component: Component, type_id: str, inherited: dict):
    return {
        'type': type_id,
        'refs': component.get_refs(),
        'location': location_to_json(component.location),
        **inherited,
    }


def composite_to_json(composite: Composite) -> dict:
    return extend_base(composite, 'composite', {
        'components': components_to_json(composite.components),
    })


def code_block_to_json(code_block: CodeBlock) -> dict:
    return extend_base(code_block, 'code-block', {
        'lang': code_block.lang,
        'content': components_to_json(code_block.contents),
    })


def table_to_json(table: Table) -> dict:
    return extend_base(table, 'table', {
        'caption': component_to_json(table.caption),
        'number': table.number,
        'rows': [
            {
                'header': row.header,
                'cells': components_to_json(row.cells),
            }
            for row in table.rows
        ]
    })


def list_to_json(list_block: ListBlock) -> dict:
    return extend_base(list_block, 'list', {
        'ordered': list_block.ordered,
        'items': components_to_json(list_block.items),
    })


def paragraph_to_json(paragraph: Paragraph) -> dict:
    return extend_base(paragraph, 'paragraph', {
        'contents': components_to_json(paragraph.contents),
    })


def plain_text_to_json(plain_text: PlainText) -> dict:
    return extend_base(plain_text, 'plain-text', {
        'content': plain_text.content,
    })


def styled_text_to_json(styled_text: StyledText) -> dict:
    return extend_base(styled_text, 'styled-text', {
        'style': styled_text.style,
        'contents': components_to_json(styled_text.contents),
    })


def custom_text_to_json(custom: CustomText) -> dict:
    return extend_base(custom, 'styled-text', {
        'custom_style': custom.custom_style,
        'contents': components_to_json(custom.contents),
    })


def link_text_to_json(link_text: LinkText) -> dict:
    return extend_base(link_text, 'link-text', {
        'reference': link_text.reference,
        'contents': components_to_json(link_text.contents),
    })


def literal_block_to_json(literal: Literal) -> dict:
    return extend_base(literal, 'literal', {
        # TODO add origin?
        'content': literal.text,
    })


def figure_to_json(figure: Figure) -> dict:
    return extend_base(figure, 'figure', {
        'number': figure.number,
        'content': component_to_json(figure.content),
        'caption': component_to_json(figure.caption),
    })


def section_to_json(section: Section) -> dict:
    return extend_base(section, 'section', {
        'level': section.level,
        'number': section.number,
        'heading': component_to_json(section.heading),
        'content': component_to_json(section.content),
    })


def toc_elements_to_json(elements: List[ElementReference]) -> List[dict]:
    return [
        {
            'title': element.title,
            'reference': element.reference,
            'number': element.number,
            'elements': toc_elements_to_json(element.elements),
        }
        for element in elements
    ]


def toc_to_json(toc: TableOfContents) -> dict:
    return extend_base(toc, 'toc', {
        'title': toc.title,
        'elements': toc_elements_to_json(toc.elements),
    })


def separator_to_json(separator: Separator) -> dict:
    return extend_base(separator, 'separator', {
        'name': separator.level,
    })


def box_to_json(box: ContentBox) -> dict:
    return extend_base(box, 'box', {
        'style': box.style,
        'content': component_to_json(box.content),
    })


def components_to_json(components: List[Component]) -> List[dict]:
    return [
        component_to_json(component)
        for component in components
    ]


def captured_text_to_json(captured: CapturedText) -> dict:
    return extend_base(captured, 'captured-text', {
        'class': captured.class_,
        'contents': components_to_json(captured.contents),
    })


def image_to_json(image: Image):
    return extend_base(image, 'image', {
        'src': image.src,
        'alt': image.alt,
    })


def function_call_to_json(call: FunctionCall):
    if call.result is None:
        raise StxError(f'Not resolved function: {call.key}', call.location)

    return component_to_json(call.result)


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
    elif isinstance(content, Paragraph):
        return paragraph_to_json(content)
    elif isinstance(content, PlainText):
        return plain_text_to_json(content)
    elif isinstance(content, StyledText):
        return styled_text_to_json(content)
    elif isinstance(content, CustomText):
        return custom_text_to_json(content)
    elif isinstance(content, LinkText):
        return link_text_to_json(content)
    elif isinstance(content, Literal):
        return literal_block_to_json(content)
    elif isinstance(content, Figure):
        return figure_to_json(content)
    elif isinstance(content, Section):
        return section_to_json(content)
    elif isinstance(content, TableOfContents):
        return toc_to_json(content)
    elif isinstance(content, Separator):
        return separator_to_json(content)
    elif isinstance(content, ContentBox):
        return box_to_json(content)
    elif isinstance(content, CapturedText):
        return captured_text_to_json(content)
    elif isinstance(content, Image):
        return image_to_json(content)
    elif isinstance(content, FunctionCall):
        return function_call_to_json(content)
    else:
        raise NotImplementedError(f'Not implemented type: {type(content)}')


def document_to_json(doc: Document) -> dict:
    return {
        'title': doc.title,
        'author': doc.author,
        'content': component_to_json(doc.content)
    }