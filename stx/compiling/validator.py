import hashlib

from stx.compiling.context import Context
from stx.components.content import CContent, CHeading, CLinkText


def build_links(context: Context, content: CContent):
    build_content(context, content)
    validate_content(context, content)


def get_id(text: str) -> str:
    return hashlib.md5(text.encode('UTF-8')).hexdigest()


def build_heading(context: Context, heading: CHeading):
    count = 0
    text = '\n'.join(heading.get_plain_text())

    while True:
        default_id = get_id(text + (str(count) if count > 0 else ''))

        if default_id in context.ids.keys():
            count += 1
        else:
            break

    context.ids[default_id] = heading

    if default_id not in heading.ids:
        heading.ids.append(default_id)


def build_content(context: Context, content: CContent):
    if isinstance(content, CHeading):
        build_heading(context, content)

    for child in content.get_children():
        build_content(context, child)


def validate_link(context: Context, link: CLinkText):
    if link.reference is not None:
        reference = link.reference
    else:
        reference = '\n'.join(link.get_plain_text())

    ref_id = get_id(reference)

    if ref_id not in context.ids.keys():
        raise Exception(f'Invalid reference: {reference}')

    link.reference = ref_id


def validate_content(context: Context, content: CContent):
    if isinstance(content, CLinkText):
        validate_link(context, content)

    for child in content.get_children():
        validate_content(context, child)
