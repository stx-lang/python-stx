from typing import List

from stx import logger, app
from stx.design.index_node import IndexNode
from stx.components import Component, Composite, CodeBlock, \
    Table, \
    ListBlock, TextBlock, RawText, PlainText, StyledText, LinkText, Figure, \
    Placeholder, Section, Separator, ContentBox
from stx.design.document import Document

from stx.rendering.html5.writer import HtmlWriter


TYPE_H_TAGS = {
    'chapter': 'h1',
    'sect1': 'h1',
    'sect2': 'h2',
    'sect3': 'h3',
    'sect4': 'h4',
    'sect5': 'h5',
}


def render_document(document: Document, writer: HtmlWriter):
    logger.info('Rendering HTML document...')

    writer.write('<!DOCTYPE html>\n')
    writer.open_tag('html')

    writer.open_tag('head')

    if document.encoding:
        writer.tag('meta', {'charset': document.encoding})

    if document.author:
        writer.tag('meta', {'name': 'author', 'content': document.author})

    writer.tag('meta', {'name': 'generator', 'content': app.title})

    if document.title:
        writer.open_tag('title')

        writer.text(document.title)

        writer.close_tag('title')

    for stylesheet in document.links.get_list('stylesheet'):
        writer.tag('link', {
            'rel': 'stylesheet',
            'type': 'text/css',
            'href': stylesheet,
        })

    writer.close_tag('head')

    writer.open_tag('body', {'data-type': 'book'})

    if document.title is not None:
        writer.open_tag('h1', inline=True)
        writer.text(document.title)
        writer.close_tag('h1', inline=True)
        writer.break_line()

    if document.header is not None:
        writer.open_tag('header')

        if document.header is not None:
            render_content(document, writer, document.header)

        writer.close_tag('header')

    render_content(document, writer, document.content)

    if document.footer is not None:
        writer.open_tag('footer')
        render_content(document, writer, document.footer)
        writer.close_tag('footer')

    writer.close_tag('body')

    writer.close_tag('html')


def render_container(document: Document, writer: HtmlWriter, container: Composite):
    render_contents(document, writer, container.components)


def render_contents(document: Document, writer: HtmlWriter, contents: List[Component]):
    for content in contents:
        render_content(document, writer, content)


def render_code_block(document: Document, writer: HtmlWriter, code: CodeBlock):
    pre_attributes = {'data-type': 'programlisting'}

    if code.lang is not None:
        pre_attributes['data-code-language'] = code.lang

    writer.open_tag('pre', inline=True, attributes=pre_attributes)
    writer.text(code.content, disable_indentation=True)
    writer.close_tag('pre', inline=True)
    writer.break_line()


def open_tag(
        document: Document,
        writer: HtmlWriter,
        content: Component,
        tag: str,
        attrs: dict):
    main_ref = document.refs.get_main_ref(content)

    if main_ref is not None:
        attrs['id'] = main_ref

    writer.open_tag(tag, attrs)

    for other_ref in document.refs.get_other_refs(content):
        writer.open_tag('a', {'id': other_ref}, inline=True)
        writer.close_tag('a', inline=True)


def render_heading(document: Document, writer: HtmlWriter, heading: Section, tag=None):
    if tag is None:
        level = heading.level

        if level < 1:
            level = 1
        elif level > 6:
            level = 6

        tag = f'h{level}'

    h_attrs = {}

    if heading.number is not None:
        h_attrs['data-number'] = heading.number

    writer.open_tag(tag, h_attrs)

    render_content(document, writer, heading.content, collapse_paragraph=True)

    writer.close_tag(tag)


def render_number(writer: HtmlWriter, number: str, css_class: str):
    writer.open_tag('span', {'class': css_class}, inline=True)
    writer.text(number)
    writer.close_tag('span', inline=True)
    writer.text(' ')


def render_table(
        document: Document,
        writer: HtmlWriter,
        table: Table):
    writer.open_tag('table')

    if table.caption is not None:
        writer.open_tag('caption')

        if table.number is not None:
            render_number(writer, table.number, 'table-number')

        render_content(document, writer, table.caption, collapse_paragraph=True)

        writer.close_tag('caption')

    for row in table.rows:
        writer.open_tag('tr')

        if row.header:
            cell_tag = 'th'
        else:
            cell_tag = 'td'

        for cell in row.cells:
            writer.open_tag(cell_tag)

            render_content(document, writer, cell, collapse_paragraph=True)

            writer.close_tag(cell_tag)

        writer.close_tag('tr')

    writer.close_tag('table')


def render_list(document: Document, writer: HtmlWriter, lst: ListBlock):
    if lst.ordered:
        tag = 'ol'
    else:
        tag = 'ul'

    writer.open_tag(tag)

    for item in lst.items:
        writer.open_tag('li')

        render_content(document, writer, item, collapse_paragraph=True)

        writer.close_tag('li')

    writer.close_tag(tag)


def render_paragraph(document: Document, writer: HtmlWriter, paragraph: TextBlock):
    open_tag(document, writer, paragraph, 'p', {})

    for content in paragraph.components:
        render_content(document, writer, content)

    writer.close_tag('p')


def render_plain_text(document: Document, writer: HtmlWriter, plain: PlainText):
    writer.text(plain.content)


def render_styled_text(document: Document, writer: HtmlWriter, styled: StyledText):
    if styled.style == 'strong':
        tag = 'strong'
    elif styled.style == 'emphasized':
        tag = 'em'
    elif styled.style == 'code':
        tag = 'code'
    else:
        tag = 'span'

    writer.open_tag(tag, inline=True)

    render_contents(document, writer, styled.contents)

    writer.close_tag(tag, inline=True)


def render_link_text(document: Document, writer: HtmlWriter, link: LinkText):
    a_attrs = {}

    if link.internal:
        a_attrs['href'] = f'#{link.reference}'
        a_attrs['data-type'] = 'xref'
    else:
        a_attrs['href'] = link.reference

    writer.open_tag('a', a_attrs, inline=True)

    render_contents(document, writer, link.contents)

    writer.close_tag('a', inline=True)


def render_embedded_text(
        document: Document, writer: HtmlWriter, embedded: RawText):
    # writer.comment(embedded.source) TODO where is comes?
    writer.write_raw(embedded.content)


def render_figure(document: Document, writer: HtmlWriter, figure: Figure):
    writer.open_tag('figure')

    render_content(document, writer, figure.content)

    writer.open_tag('figcaption')

    if figure.number is not None:
        render_number(writer, figure.number, 'figure-number')

    render_content(document, writer, figure.caption, collapse_paragraph=True)

    writer.close_tag('figcaption')

    writer.close_tag('figure')


def render_placeholder(document: Document, writer: HtmlWriter, content: Placeholder):
    if content.name == 'toc':
        render_toc(document, writer, content)
    else:
        raise Exception(f'Not implemented placeholder: {content.name}')


def render_section(document: Document, writer: HtmlWriter, section: Section):
    section_attrs = {}

    if section.type is not None:
        section_attrs['data-type'] = section.type

    h_id = document.refs.get_main_ref(section.heading)

    if h_id is not None:
        section_attrs['id'] = h_id

    writer.open_tag('section', section_attrs)

    if section.type in TYPE_H_TAGS:
        h_tag = TYPE_H_TAGS[section.type]
    else:
        h_tag = None

    render_heading(document, writer, section.heading, h_tag)

    for component in section.components:
        render_content(document, writer, component)

    writer.close_tag('section')


def render_separator(document: Document, writer: HtmlWriter, separator: Separator):
    writer.tag('hr', {'data-level': separator.level})


def render_box(document: Document, writer: HtmlWriter, box: ContentBox):
    writer.open_tag('div', {'data-type': box.style})
    render_content(document, writer, box.content)
    writer.close_tag('div')


def render_content(
        document: Document,
        writer: HtmlWriter,
        content: Component,
        collapse_paragraph=False):
    if collapse_paragraph and isinstance(content, TextBlock):
        render_contents(document, writer, content.components)
    elif isinstance(content, Composite):
        render_container(document, writer, content)
    elif isinstance(content, CodeBlock):
        render_code_block(document, writer, content)
    elif isinstance(content, Table):
        render_table(document, writer, content)
    elif isinstance(content, ListBlock):
        render_list(document, writer, content)
    elif isinstance(content, TextBlock):
        render_paragraph(document, writer, content)
    elif isinstance(content, PlainText):
        render_plain_text(document, writer, content)
    elif isinstance(content, StyledText):
        render_styled_text(document, writer, content)
    elif isinstance(content, LinkText):
        render_link_text(document, writer, content)
    elif isinstance(content, RawText):
        render_embedded_text(document, writer, content)
    elif isinstance(content, Figure):
        render_figure(document, writer, content)
    elif isinstance(content, Section):
        render_section(document, writer, content)
    elif isinstance(content, Placeholder):
        render_placeholder(document, writer, content)
    elif isinstance(content, Separator):
        render_separator(document, writer, content)
    elif isinstance(content, ContentBox):
        render_box(document, writer, content)
    else:
        raise NotImplementedError()


def render_toc(document: Document, writer: HtmlWriter, content: Placeholder):
    writer.open_tag('nav', {'id': 'toc', 'data-type': 'toc'})

    title = content.attributes.get_value('title')

    if title is not None:
        writer.open_tag('h1', inline=True)
        writer.text(title)
        writer.close_tag('h1')

    render_index_nodes(document, writer, document.index)

    writer.close_tag('nav')


def render_index_nodes(
        document: Document, writer: HtmlWriter, nodes: List[IndexNode]):
    if len(nodes) == 0:
        return

    writer.open_tag('ol')

    for node in nodes:
        writer.open_tag('li')

        ref = document.refs.get_main_ref(node.heading)

        a_attrs = {}

        if ref is not None:
            a_attrs['href'] = f'#{ref}'

        if node.heading.number is not None:
            a_attrs['data-number'] = node.heading.number

        writer.open_tag('a', a_attrs, inline=True)

        render_content(
            document, writer, node.heading.content, collapse_paragraph=True)

        writer.close_tag('a', inline=True)
        writer.break_line()

        if len(node.nodes) > 0:
            render_index_nodes(document, writer, node.nodes)

        writer.close_tag('li')

    writer.close_tag('ol')
