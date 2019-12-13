from typing import List, Optional

from stx.compiling.context import Context
from stx.compiling.index_node import IndexNode
from stx.components.content import CContent, CContainer, CCodeBlock, CHeading, \
    CTable, CList, CParagraph, CRawText, CTableRow, CPlainText, CStyledText, \
    CLinkText, CEmbeddedText, CFigure
from stx.writting import HtmlWriter


def render_document(context: Context, writer: HtmlWriter, content: CContent):
    writer.write('<!DOCTYPE html>\n')
    writer.open_tag('html')

    writer.open_tag('head')

    writer.tag('meta', {'author': 'generator', 'content': 'Sergio Pedraza'})
    writer.tag('meta', {'name': 'generator', 'content': 'STX 0.0.1'})

    writer.open_tag('title')

    writer.text(' '.join(context.index[0].heading.get_plain_text()))

    writer.close_tag('title')

    for href in context.linked_stylesheets:
        writer.tag('link', {
            'rel': 'stylesheet',
            'href': href,
        })

    writer.close_tag('head')

    writer.open_tag('body')

    render_index(context, writer)

    writer.open_tag('main')

    render_content(context, writer, content)

    writer.close_tag('main')

    writer.close_tag('body')

    writer.close_tag('html')


def render_container(context: Context, writer: HtmlWriter, container: CContainer):
    render_contents(context, writer, container.contents)


def render_contents(context: Context, writer: HtmlWriter, contents: List[CContent]):
    for content in contents:
        render_content(context, writer, content)


def render_code_block(context: Context, writer: HtmlWriter, code: CCodeBlock):
    pre_attributes = {}

    css_classes = code.attributes.get_list('source')

    if len(css_classes) > 0:
        pre_attributes['class'] = ' '.join(css_classes)

    writer.open_tag('pre', inline=True, attributes=pre_attributes)
    writer.text(code.text, disable_indentation=True)
    writer.close_tag('pre', inline=True)
    writer.break_line()


def open_tag(
        context: Context,
        writer: HtmlWriter,
        content: CContent,
        tag: str,
        attrs: dict):
    main_ref = context.links.get_main_ref(content)

    if main_ref is not None:
        attrs['id'] = main_ref

    writer.open_tag(tag, attrs)

    for other_ref in context.links.get_other_refs(content):
        writer.open_tag('a', {'id': other_ref}, inline=True)
        writer.close_tag('a', inline=True)


def render_heading(context: Context, writer: HtmlWriter, heading: CHeading):
    level = heading.level

    if level < 1:
        level = 1
    elif level > 6:
        level = 6

    tag = f'h{level}'
    attrs = {}

    open_tag(context, writer, heading, tag, attrs)

    if heading.number is not None:
        writer.open_tag('span', inline=True)
        writer.text(heading.number)
        writer.text(' ')
        writer.close_tag('span', inline=True)

    render_content(context, writer, heading.content, collapse_paragraph=True)

    writer.close_tag(tag)


def render_table(
        context: Context,
        writer: HtmlWriter,
        table: CTable):
    writer.open_tag('table')

    if table.caption is not None:
        writer.open_tag('caption')

        if table.number is not None:
            writer.open_tag('span', {'class': 'stx-number'}, inline=True)
            writer.text(table.number)
            writer.close_tag('span', inline=True)
            writer.text(' ')

        render_content(context, writer, table.caption, collapse_paragraph=True)

        writer.close_tag('caption')

    for row in table.rows:
        writer.open_tag('tr')

        if row.header:
            cell_tag = 'th'
        else:
            cell_tag = 'td'

        for cell in row.cells:
            writer.open_tag(cell_tag)

            render_content(context, writer, cell.content, collapse_paragraph=True)

            writer.close_tag(cell_tag)

        writer.close_tag('tr')

    writer.close_tag('table')


def render_list(context: Context, writer: HtmlWriter, lst: CList):
    if lst.ordered:
        tag = 'ol'
    else:
        tag = 'ul'

    writer.open_tag(tag)

    for item in lst.items:
        writer.open_tag('li')

        render_content(context, writer, item.content, collapse_paragraph=True)

        writer.close_tag('li')

    writer.close_tag(tag)


def render_paragraph(context: Context, writer: HtmlWriter, paragraph: CParagraph):
    open_tag(context, writer, paragraph, 'p', {})

    for content in paragraph.contents:
        render_content(context, writer, content)

    writer.close_tag('p')


def render_raw(context: Context, writer: HtmlWriter, raw: CRawText):
    for line in raw.lines:
        writer.text(line)
        writer.text('\n')


def render_plain_text(context: Context, writer: HtmlWriter, plain: CPlainText):
    writer.text(plain.text)


def render_styled_text(context: Context, writer: HtmlWriter, styled: CStyledText):
    if styled.style == 'strong':
        tag = 'strong'
    elif styled.style == 'emphasized':
        tag = 'em'
    elif styled.style == 'code':
        tag = 'code'
    else:
        tag = 'span'

    writer.open_tag(tag, inline=True)

    render_contents(context, writer, styled.contents)

    writer.close_tag(tag, inline=True)


def render_link_text(context: Context, writer: HtmlWriter, link: CLinkText):
    if link.internal:
        href = f'#{link.reference}'
    else:
        href = link.reference

    writer.open_tag('a', {
        'href': href,
    }, inline=True)

    render_contents(context, writer, link.contents)

    writer.close_tag('a', inline=True)


def render_embedded_text(
        context: Context, writer: HtmlWriter, embedded: CEmbeddedText):
    writer.comment(embedded.source)
    writer.write_raw(embedded.text)


def render_figure(context: Context, writer: HtmlWriter, figure: CFigure):
    writer.open_tag('figure')

    render_content(context, writer, figure.content)

    writer.open_tag('figcaption')

    if figure.number is not None:
        writer.open_tag('span', {'class': 'stx-number'}, inline=True)
        writer.text(figure.number)
        writer.close_tag('span', inline=True)
        writer.text(' ')

    render_content(context, writer, figure.caption, collapse_paragraph=True)

    writer.close_tag('figcaption')

    writer.close_tag('figure')


def render_content(
        context: Context,
        writer: HtmlWriter,
        content: CContent,
        collapse_paragraph=False):
    if collapse_paragraph and isinstance(content, CParagraph):
        render_contents(context, writer, content.contents)
    elif isinstance(content, CContainer):
        render_container(context, writer, content)
    elif isinstance(content, CCodeBlock):
        render_code_block(context, writer, content)
    elif isinstance(content, CHeading):
        render_heading(context, writer, content)
    elif isinstance(content, CTable):
        render_table(context, writer, content)
    elif isinstance(content, CList):
        render_list(context, writer, content)
    elif isinstance(content, CParagraph):
        render_paragraph(context, writer, content)
    elif isinstance(content, CPlainText):
        render_plain_text(context, writer, content)
    elif isinstance(content, CStyledText):
        render_styled_text(context, writer, content)
    elif isinstance(content, CLinkText):
        render_link_text(context, writer, content)
    elif isinstance(content, CRawText):
        render_raw(context, writer, content)
    elif isinstance(content, CEmbeddedText):
        render_embedded_text(context, writer, content)
    elif isinstance(content, CFigure):
        render_figure(context, writer, content)
    else:
        raise NotImplementedError()


def render_index(context: Context, writer: HtmlWriter):
    writer.open_tag('nav', {'class': 'toc'})

    render_index_nodes(context, writer, context.index)

    writer.close_tag('nav')


def render_index_nodes(
        context: Context, writer: HtmlWriter, nodes: List[IndexNode]):
    if len(nodes) == 0:
        return

    writer.open_tag('ol')

    for node in nodes:
        ref = context.links.get_main_ref(node.heading)

        a_attrs = {}

        if ref is not None:
            a_attrs['href'] = f'#{ref}'

        writer.open_tag('li')

        writer.open_tag('a', a_attrs, inline=True)

        if node.heading.number is not None:
            writer.text(node.heading.number)
            writer.text(' ')

        render_content(
            context, writer, node.heading.content, collapse_paragraph=True)

        writer.close_tag('a', inline=True)
        writer.break_line()

        render_index_nodes(context, writer, node.nodes)

        writer.close_tag('li')

    writer.close_tag('ol')
