from typing import List, Optional

from stx import logger
from stx.compiling.index_node import IndexNode
from stx.v2.components import Component, Composite, CodeBlock, Heading, Table, \
    ListBlock, TextBlock, RawText, PlainText, StyledText, LinkText, Figure
from stx.v2.document import Document

from stx.writting import HtmlWriter


def render_document(document: Document, writer: HtmlWriter):
    logger.info('Rendering HTML document...')

    writer.write('<!DOCTYPE html>\n')
    writer.open_tag('html')

    writer.open_tag('head')

    writer.tag('meta', {'author': 'generator', 'content': 'Sergio Pedraza'})
    writer.tag('meta', {'name': 'generator', 'content': 'STX 0.0.1'})

    writer.open_tag('title')

    # TODO improve this
    writer.text(document.index[0].heading.get_text())

    writer.close_tag('title')

    for stylesheet in document.links.get_list('stylesheet'):
        writer.tag('link', {
            'rel': 'stylesheet',
            'type': 'text/css',
            'href': stylesheet,
        })

    writer.close_tag('head')

    writer.open_tag('body')

    render_index(document, writer)

    writer.open_tag('main')

    render_content(document, writer, document.content)

    writer.close_tag('main')

    writer.close_tag('body')

    writer.close_tag('html')


def render_container(document: Document, writer: HtmlWriter, container: Composite):
    render_contents(document, writer, container.components)


def render_contents(document: Document, writer: HtmlWriter, contents: List[Component]):
    for content in contents:
        render_content(document, writer, content)


def render_code_block(document: Document, writer: HtmlWriter, code: CodeBlock):
    pre_attributes = {}

    css_classes = code.attributes.get_list('source')

    if len(css_classes) > 0:
        pre_attributes['class'] = ' '.join(css_classes)

    writer.open_tag('pre', inline=True, attributes=pre_attributes)
    writer.text(code.code, disable_indentation=True)
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


def render_heading(document: Document, writer: HtmlWriter, heading: Heading):
    level = heading.level

    if level < 1:
        level = 1
    elif level > 6:
        level = 6

    tag = f'h{level}'
    attrs = {}

    open_tag(document, writer, heading, tag, attrs)

    if heading.number is not None:
        writer.open_tag('span', inline=True)
        writer.text(heading.number)
        writer.text(' ')
        writer.close_tag('span', inline=True)

    render_content(document, writer, heading.content, collapse_paragraph=True)

    writer.close_tag(tag)


def render_table(
        document: Document,
        writer: HtmlWriter,
        table: Table):
    writer.open_tag('table')

    if table.caption is not None:
        writer.open_tag('caption')

        if table.number is not None:
            writer.open_tag('span', {'class': 'stx-number'}, inline=True)
            writer.text(table.number)
            writer.close_tag('span', inline=True)
            writer.text(' ')

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


def render_raw(document: Document, writer: HtmlWriter, raw: RawText):
    writer.text(raw.text)  # TODO to delete?


def render_plain_text(document: Document, writer: HtmlWriter, plain: PlainText):
    writer.text(plain.text)


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
    if link.internal:
        href = f'#{link.reference}'
    else:
        href = link.reference

    writer.open_tag('a', {
        'href': href,
    }, inline=True)

    render_contents(document, writer, link.contents)

    writer.close_tag('a', inline=True)


def render_embedded_text(
        document: Document, writer: HtmlWriter, embedded: RawText):
    # writer.comment(embedded.source) TODO where is comes?
    writer.write_raw(embedded.text)


def render_figure(document: Document, writer: HtmlWriter, figure: Figure):
    writer.open_tag('figure')

    render_content(document, writer, figure.content)

    writer.open_tag('figcaption')

    if figure.number is not None:
        writer.open_tag('span', {'class': 'stx-number'}, inline=True)
        writer.text(figure.number)
        writer.close_tag('span', inline=True)
        writer.text(' ')

    render_content(document, writer, figure.caption, collapse_paragraph=True)

    writer.close_tag('figcaption')

    writer.close_tag('figure')


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
    elif isinstance(content, Heading):
        render_heading(document, writer, content)
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
    else:
        raise NotImplementedError()


def render_index(document: Document, writer: HtmlWriter):
    writer.open_tag('nav', {'class': 'toc'})

    render_index_nodes(document, writer, document.index)

    writer.close_tag('nav')


def render_index_nodes(
        document: Document, writer: HtmlWriter, nodes: List[IndexNode]):
    if len(nodes) == 0:
        return

    writer.open_tag('ol')

    for node in nodes:
        ref = document.refs.get_main_ref(node.heading)

        a_attrs = {}

        if ref is not None:
            a_attrs['href'] = f'#{ref}'

        writer.open_tag('li')

        writer.open_tag('a', a_attrs, inline=True)

        if node.heading.number is not None:
            writer.text(node.heading.number)
            writer.text(' ')

        render_content(
            document, writer, node.heading.content, collapse_paragraph=True)

        writer.close_tag('a', inline=True)
        writer.break_line()

        render_index_nodes(document, writer, node.nodes)

        writer.close_tag('li')

    writer.close_tag('ol')
