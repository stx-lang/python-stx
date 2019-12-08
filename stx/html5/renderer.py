from typing import List

from stx.components.content import CContent, CContainer, CCodeBlock, CHeading, \
    CTable, CList, CParagraph, CRawText, CTableRow, CPlainText, CStyledText, \
    CLinkText
from stx.writting import HtmlWriter


def render_document(writer: HtmlWriter, content: CContent):
    writer.write('<!DOCTYPE html>\n')
    writer.open_tag('html')

    writer.open_tag('head')

    writer.open_tag('title')
    writer.text('STX\n')
    writer.close_tag('title')

    writer.close_tag('head')

    writer.open_tag('body')

    writer.open_tag('main')

    render_content(writer, content)

    writer.close_tag('main')

    writer.close_tag('body')

    writer.close_tag('html')


def render_container(writer: HtmlWriter, container: CContainer):
    render_contents(writer, container.contents)


def render_contents(writer: HtmlWriter, contents: List[CContent]):
    for content in contents:
        render_content(writer, content)


def render_code_block(writer: HtmlWriter, code: CCodeBlock):
    writer.open_tag('pre')
    writer.text(code.text)
    writer.close_tag('pre')


def render_heading(writer: HtmlWriter, heading: CHeading):
    level = heading.level

    if level < 1:
        level = 1
    elif level > 6:
        level = 6

    tag = f'h{level}'
    writer.open_tag(tag)

    render_content(writer, heading.content, collapse_paragraph=True)

    writer.close_tag(tag)


def render_table(writer: HtmlWriter, table: CTable):
    writer.open_tag('table')

    for row in table.rows:
        writer.open_tag('tr')

        if row.header:
            cell_tag = 'th'
        else:
            cell_tag = 'td'

        for cell in row.cells:
            writer.open_tag(cell_tag)

            render_content(writer, cell.content, collapse_paragraph=True)

            writer.close_tag(cell_tag)

        writer.close_tag('tr')

    writer.close_tag('table')


def render_list(writer: HtmlWriter, lst: CList):
    if lst.ordered:
        tag = 'ol'
    else:
        tag = 'ul'

    writer.open_tag(tag)

    for item in lst.items:
        writer.open_tag('li')

        render_content(writer, item.content, collapse_paragraph=True)

        writer.close_tag('li')

    writer.close_tag(tag)


def render_paragraph(writer: HtmlWriter, paragraph: CParagraph):
    writer.open_tag('p')

    for content in paragraph.contents:
        render_content(writer, content)

    writer.close_tag('p')


def render_raw(writer: HtmlWriter, raw: CRawText):
    for line in raw.lines:
        writer.text(line)
        writer.text('\n')


def render_plain_text(writer: HtmlWriter, plain: CPlainText):
    writer.text(plain.text)


def render_styled_text(writer: HtmlWriter, styled: CStyledText):
    if styled.style == 'bold':
        tag = 'strong'
    else:
        tag = 'span'

    writer.open_tag(tag)

    render_content(writer, styled.content)

    writer.close_tag(tag)


def render_link_text(writer: HtmlWriter, link: CLinkText):
    writer.open_tag('a', {
        'href': link.reference,
    })

    render_content(writer, link.content)

    writer.close_tag('a')


def render_content(
        writer: HtmlWriter,
        content: CContent,
        collapse_paragraph=False):
    if collapse_paragraph and isinstance(content, CParagraph):
        render_contents(writer, content.contents)
    elif isinstance(content, CContainer):
        render_container(writer, content)
    elif isinstance(content, CCodeBlock):
        render_code_block(writer, content)
    elif isinstance(content, CHeading):
        render_heading(writer, content)
    elif isinstance(content, CTable):
        render_table(writer, content)
    elif isinstance(content, CList):
        render_list(writer, content)
    elif isinstance(content, CParagraph):
        render_paragraph(writer, content)
    elif isinstance(content, CPlainText):
        render_plain_text(writer, content)
    elif isinstance(content, CStyledText):
        render_styled_text(writer, content)
    elif isinstance(content, CLinkText):
        render_link_text(writer, content)
    elif isinstance(content, CRawText):
        render_raw(writer, content)
    else:
        raise NotImplementedError()
