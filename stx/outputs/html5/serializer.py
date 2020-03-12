from typing import List

from stx import app, logger
from stx.components import Component, Composite, CodeBlock, Table, Image, \
    FunctionCall, CustomText, Layout
from stx.components import ListBlock, Paragraph, PlainText, StyledText
from stx.components import LinkText, Literal, Figure, Section, Separator
from stx.components import ContentBox, TableOfContents, ElementReference
from stx.components import CapturedText
from stx.document import Document
from stx.outputs.html5.dom import Tag
from stx.utils.stx_error import StxError
from stx.utils.debug import see

TYPE_H_TAGS = {
    'chapter': 'h1',
    'sect1': 'h1',
    'sect2': 'h2',
    'sect3': 'h3',
    'sect4': 'h4',
    'sect5': 'h5',
}

CAPTURED_CLASS_TAGS = [
    'cite', 'ins', 'kbd', 'mark', 'q', 's',
    'samp', 'small', 'sub', 'sup', 'var',
]


def document_to_html(document: Document) -> List[Tag]:
    logger.info('Serializing HTML5 book...')

    html = Tag('html')

    generate_head(document, html)

    generate_body(document, html)

    return [Tag('!DOCTYPE html'), html]


def generate_head(document: Document, html: Tag):
    head = html.append_tag('head')

    if document.encoding:
        head.append_tag('meta', {'charset': document.encoding})

    if document.author:
        head.append_tag('meta', {
            'name': 'author',
            'content': document.author,
        })

    head.append_tag('meta', {
        'name': 'generator',
        'content': app.title,
    })

    if document.title:
        head.append_tag('title', text=document.title)

    for stylesheet in document.stylesheets:
        head.append_tag('link', {
            'rel': 'stylesheet',
            'type': 'text/css',
            'href': stylesheet,
        })


def generate_body(document: Document, html: Tag):
    body = html.append_tag('body', {'data-type': 'book'})

    if document.title is not None:
        body.append_tag('h1', text=document.title)

    if document.header is not None:
        header = body.append_tag('header')

        generate_component(header, document.header)

    if document.content is not None:
        generate_component(body, document.content)

    if document.footer is not None:
        footer = body.append_tag('footer')

        generate_component(footer, document.footer)


def generate_component(
        parent: Tag, component: Component,
        collapse_paragraph=False,
        collapse_section=False):
    if isinstance(component, Composite):
        generate_components(parent, component.components)
    elif isinstance(component, CodeBlock):
        generate_code_block(parent, component)
    elif isinstance(component, Table):
        generate_table(parent, component)
    elif isinstance(component, ListBlock):
        generate_list_block(parent, component)
    elif isinstance(component, Paragraph):
        generate_paragraph(parent, component, collapse_paragraph)
    elif isinstance(component, PlainText):
        generate_plain_text(parent, component)
    elif isinstance(component, StyledText):
        generate_styled_text(parent, component)
    elif isinstance(component, CustomText):
        generate_custom_text(parent, component)
    elif isinstance(component, LinkText):
        generate_link_text(parent, component)
    elif isinstance(component, CapturedText):
        generate_captured_text(parent, component)
    elif isinstance(component, Literal):
        generate_literal(parent, component)
    elif isinstance(component, Figure):
        generate_figure(parent, component)
    elif isinstance(component, Section):
        generate_section(parent, component, collapse_section)
    elif isinstance(component, TableOfContents):
        generate_toc(parent, component)
    elif isinstance(component, Separator):
        generate_separator(parent, component)
    elif isinstance(component, ContentBox):
        generate_box(parent, component)
    elif isinstance(component, Image):
        generate_image(parent, component)
    elif isinstance(component, FunctionCall):
        generate_function_call(parent, component)
    elif isinstance(component, Layout):
        generate_layout(parent, component)
    else:
        raise NotImplementedError(f'Not implemented type: {type(component)}')


def generate_components(parent: Tag, components: List[Component]):
    for child in components:
        generate_component(parent, child)


def generate_code_block(parent: Tag, code_block: CodeBlock):
    pre = append_component_tag(parent, code_block, 'pre')

    pre.preserve_spaces = True

    pre['data-type'] = 'programlisting'

    if code_block.lang is not None:
        pre['data-code-language'] = code_block.lang

    generate_components(pre, code_block.contents)


def generate_table(parent: Tag, table: Table):
    table_tag = append_component_tag(parent, table, 'table')

    if table.caption is not None:
        caption_tag = table_tag.append_tag('caption')

        if table.number is not None:
            caption_tag['data-number'] = table.number

        generate_component(
            caption_tag, table.caption, collapse_paragraph=True)

    for row in table.rows:
        row_tag = table_tag.append_tag('tr')

        if row.header:
            cell_tag_name = 'th'
        else:
            cell_tag_name = 'td'

        for cell in row.cells:
            cell_tag = row_tag.append_tag(cell_tag_name)

            generate_component(cell_tag, cell, collapse_paragraph=True)


def generate_list_block(parent: Tag, list_block: ListBlock):
    if list_block.ordered:
        list_tag_name = 'ol'
    else:
        list_tag_name = 'ul'

    list_tag = append_component_tag(parent, list_block, list_tag_name)

    for item in list_block.items:
        item_tag = list_tag.append_tag('li')

        generate_component(item_tag, item, collapse_paragraph=True)


def generate_paragraph(parent: Tag, paragraph: Paragraph, collapse: bool):
    if not collapse:
        p_tag = append_component_tag(parent, paragraph, 'p')
    else:
        p_tag = parent

    generate_components(p_tag, paragraph.contents)


def generate_plain_text(parent: Tag, plain_text: PlainText):
    for ref in plain_text.get_refs():
        parent.append_tag('a', {'id': ref}, text='')

    parent.append_text(plain_text.content)


def generate_styled_text(parent: Tag, styled_text: StyledText):
    if styled_text.style == 'strong':
        tag_name = 'strong'
    elif styled_text.style == 'emphasized':
        tag_name = 'em'
    elif styled_text.style == 'code':
        tag_name = 'code'
    elif styled_text.style == 'deleted':
        tag_name = 'del'
    else:
        tag_name = None

    if tag_name is not None:
        styled_tag = append_component_tag(parent, styled_text, tag_name)

        generate_components(styled_tag, styled_text.contents)
    else:
        if styled_text.style == 'double-quote':
            parent.append_literal('&ldquo;')
            generate_components(parent, styled_text.contents)
            parent.append_literal('&rdquo;')
        elif styled_text.style == 'single-quote':
            parent.append_literal('&lsquo;')
            generate_components(parent, styled_text.contents)
            parent.append_literal('&rsquo;')
        else:
            raise StxError(
                f'Not supported style: {styled_text.style}.',
                styled_text.location)


def generate_custom_text(parent: Tag, styled_text: CustomText):
    styled_tag = append_component_tag(parent, styled_text, 'span')

    if styled_text.custom_style is not None:
        styled_tag['class'] = styled_text.custom_style

    generate_components(styled_tag, styled_text.contents)


def generate_link_text(parent: Tag, link_text: LinkText):
    a_tag = append_component_tag(parent, link_text, 'a')

    if link_text.is_internal():
        a_tag['href'] = f'#{link_text.reference}'
        a_tag['data-type'] = 'xref'
    elif link_text.is_external():
        a_tag['href'] = link_text.reference

    if link_text.invalid:
        a_tag['data-status'] = 'invalid'

    generate_components(a_tag, link_text.contents)


def generate_captured_text(parent: Tag, captured: CapturedText):
    if captured.class_ in CAPTURED_CLASS_TAGS:
        cap_tag = append_component_tag(parent, captured, captured.class_)
    else:
        cap_tag = append_component_tag(parent, captured, 'span')

        if captured.class_:
            cap_tag['class'] = captured.class_

    generate_components(cap_tag, captured.contents)


def generate_literal(parent: Tag, literal: Literal):
    parent.append_literal(literal.text)


def generate_figure(parent: Tag, figure: Figure):
    figure_tag = append_component_tag(parent, figure, 'figure')

    generate_component(figure_tag, figure.content)

    caption_tag = figure_tag.append_tag('figcaption')

    if figure.number is not None:
        caption_tag['data-number'] = figure.number

    generate_component(caption_tag, figure.caption, collapse_paragraph=True)


def generate_section(parent: Tag, section: Section, collapse: bool):
    if not collapse:
        section_tag = append_component_tag(parent, section, 'section')
    else:
        section_tag = parent

    if section.type is not None:
        section_tag['data-type'] = section.type

    if section.type in TYPE_H_TAGS:
        h_tag_name = TYPE_H_TAGS[section.type]
    else:
        level = section.level

        if level < 1:
            level = 1
        elif level > 6:
            level = 6

        h_tag_name = f'h{level}'

    h_tag = section_tag.append_tag(h_tag_name)

    if section.number is not None:
        h_tag['data-number'] = section.number

    generate_component(h_tag, section.heading, collapse_paragraph=True)

    generate_component(section_tag, section.content)


def generate_toc(parent: Tag, toc: TableOfContents):
    nav_tag = append_component_tag(parent, toc, 'nav')
    nav_tag['data-type'] = 'toc'

    if toc.title is not None:
        nav_tag.append_tag('h1', text=toc.title)

    generate_toc_elements(nav_tag, toc.elements)


def generate_toc_elements(parent: Tag, elements: List[ElementReference]):
    if len(elements) == 0:
        return

    list_tag = parent.append_tag('ol')

    for element in elements:
        item_tag = list_tag.append_tag('li')

        a_tag = item_tag.append_tag('a', {
            'href': f'#{element.reference}',
            'data-type': 'xref',
        }, text=element.title)

        if element.number is not None:
            a_tag['data-number'] = element.number

        generate_toc_elements(item_tag, element.elements)


def generate_separator(parent: Tag, separator: Separator):
    sep = append_component_tag(parent, separator, 'hr')
    sep['data-level'] = separator.level


def generate_box(parent: Tag, box: ContentBox):
    box_tag = append_component_tag(parent, box, 'div')

    if box.style is not None:
        box_tag['data-type'] = box.style

    generate_component(box_tag, box.content, collapse_section=True)


def generate_image(parent: Tag, image: Image):
    img_tag = parent.append_tag('img')
    img_tag['src'] = image.src

    if image.alt:
        img_tag['alt'] = image.alt


def generate_function_call(parent: Tag, call: FunctionCall):
    if call.result is None:
        raise StxError(
            f'Function {call.key} was not processed.', call.location)

    generate_component(parent, call.result)


def generate_layout(parent: Tag, layout: Layout):
    container = parent.append_tag('div', {
        'data-type': 'layout',
        'data-dir': layout.direction,
    })

    for component in layout.components:
        item = container.append_tag('div', {
            'data-type': 'layout-item',
        })

        generate_component(item, component)


def append_component_tag(
        parent: Tag, component: Component, tag_name: str) -> Tag:
    for other_id in reversed(component.get_other_refs()):
        parent.append_tag('a', {'id': other_id}, text='')

    tag = parent.append_tag(tag_name)

    tag_id = component.get_main_ref()

    if tag_id is not None:
        tag['id'] = tag_id

    return tag

