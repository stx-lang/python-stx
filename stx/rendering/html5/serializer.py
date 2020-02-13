from typing import Optional, List

from stx import app, logger
from stx.compiling.reading.location import Location
from stx.components import Component, Composite, CodeBlock, Table, \
    ListBlock, Paragraph, PlainText, StyledText, LinkText, RawText, Figure, \
    Section, Separator, ContentBox, TableOfContents, ElementReference
from stx.document import Document
from stx.rendering.html5.dom import Tag

TYPE_H_TAGS = {
    'chapter': 'h1',
    'sect1': 'h1',
    'sect2': 'h2',
    'sect3': 'h3',
    'sect4': 'h4',
    'sect5': 'h5',
}


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
        parent: Tag, component: Component, collapse_paragraph=False):
    if collapse_paragraph and isinstance(component, Paragraph):
        generate_components(parent, component.contents)
    elif isinstance(component, Composite):
        generate_components(parent, component.components)
    elif isinstance(component, CodeBlock):
        generate_code_block(parent, component)
    elif isinstance(component, Table):
        generate_table(parent, component)
    elif isinstance(component, ListBlock):
        generate_list_block(parent, component)
    elif isinstance(component, Paragraph):
        generate_paragraph(parent, component)
    elif isinstance(component, PlainText):
        generate_plain_text(parent, component)
    elif isinstance(component, StyledText):
        generate_styled_text(parent, component)
    elif isinstance(component, LinkText):
        generate_link_text(parent, component)
    elif isinstance(component, RawText):
        generate_embedded_block(parent, component)
    elif isinstance(component, Figure):
        generate_figure(parent, component)
    elif isinstance(component, Section):
        generate_section(parent, component)
    elif isinstance(component, TableOfContents):
        generate_toc(parent, component)
    elif isinstance(component, Separator):
        generate_separator(parent, component)
    elif isinstance(component, ContentBox):
        generate_box(parent, component)
    else:
        raise NotImplementedError(f'Not implemented type: {type(component)}')


def generate_components(parent: Tag, components: List[Component]):
    for child in components:
        generate_component(parent, child)


def generate_code_block(parent: Tag, code_block: CodeBlock):
    pre = parent.append_tag('pre')
    pre.preserve_spaces = True

    pre['data-type'] = 'programlisting'

    if code_block.lang is not None:
        pre['data-code-language'] = code_block.lang

    pre.append_text(code_block.content)


def generate_table(parent: Tag, table: Table):
    table_tag = parent.append_tag('table')

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

    list_tag = parent.append_tag(list_tag_name)

    for item in list_block.items:
        item_tag = list_tag.append_tag('li')

        generate_component(item_tag, item, collapse_paragraph=True)


def generate_paragraph(parent: Tag, paragraph: Paragraph):
    p_tag = parent.append_tag('p')

    generate_components(p_tag, paragraph.contents)


def generate_plain_text(parent: Tag, plain_text: PlainText):
    parent.append_text(plain_text.content)


def generate_styled_text(parent: Tag, styled_text: StyledText):
    if styled_text.style == 'strong':
        tag_name = 'strong'
    elif styled_text.style == 'emphasized':
        tag_name = 'em'
    elif styled_text.style == 'code':
        tag_name = 'code'
    else:
        tag_name = 'span'

    styled_tag = parent.append_tag(tag_name)

    generate_components(styled_tag, styled_text.contents)


def generate_link_text(parent: Tag, link_text: LinkText):
    a_tag = parent.append_tag('a')

    if link_text.is_internal():
        a_tag['href'] = f'#{link_text.reference}'
        a_tag['data-type'] = 'xref'
    elif link_text.is_external():
        a_tag['href'] = link_text.reference

    generate_components(a_tag, link_text.contents)


def generate_embedded_block(parent: Tag, embedded_block: RawText):
    parent.append_literal(embedded_block.content)


def generate_figure(parent: Tag, figure: Figure):
    figure_tag = parent.append_tag('figure')

    generate_component(figure_tag, figure.content)

    caption_tag = figure_tag.append_tag('figcaption')

    if figure.number is not None:
        caption_tag['data-number'] = figure.number

    generate_component(caption_tag, figure.caption, collapse_paragraph=True)


def generate_section(parent: Tag, section: Section):
    section_tag = parent.append_tag('section')

    section_id = section.get_main_ref()

    if section_id is not None:
        section_tag['id'] = section_id

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
    nav_tag = parent.append_tag('nav', {'data-type': 'toc'})

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
    parent.append_tag('hr', {'data-level': separator.level})


def generate_box(parent: Tag, box: ContentBox):
    box_tag = parent.append_tag('div', {'data-type': box.style})
    generate_component(box_tag, box.content)
