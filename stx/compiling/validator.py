import hashlib
import re

from stx.compiling.context import Context
from stx.components.content import CContent, CHeading, CLinkText
from stx.link_map import make_ref


def build_links(context: Context, content: CContent):
    consume_ref_attribute(context, content)
    build_content(context, content)
    validate_content(context, content)


def consume_ref_attribute(context: Context, content: CContent):
    for child in content.walk():
        refs = child.attributes.get_list('ref')

        for ref in refs:
            ref = make_ref(ref)

            context.links.register_ref(ref, child)


def build_heading(context: Context, heading: CHeading):
    context.links.register_content(heading, main=True)


def build_content(context: Context, content: CContent):
    if isinstance(content, CHeading):
        build_heading(context, content)

    for child in content.get_children():
        build_content(context, child)


def validate_link(context: Context, link: CLinkText):
    if link.reference is not None and not link.internal:
        return

    if link.reference is not None:
        reference = link.reference
    else:
        reference = '\n'.join(link.get_plain_text())

    ref = make_ref(reference)

    if not context.links.contains_ref(ref):
        print(f'WARNING: Invalid reference: {reference}')

    link.reference = ref


def validate_content(context: Context, content: CContent):
    if isinstance(content, CLinkText):
        validate_link(context, content)

    for child in content.get_children():
        validate_content(context, child)
