import hashlib
from typing import List, Dict

from stx.components.content import CContent, CContainer, CHeading, CLinkText

IDsMap = Dict[str, CContent]


def build_links(content: CContent):
    ids = {}

    build_content(ids, content)
    validate_content(ids, content)


def get_id(text: str) -> str:
    return hashlib.md5(text.encode('UTF-8')).hexdigest()


def build_heading(ids: IDsMap, heading: CHeading):
    count = 0
    text = '\n'.join(heading.get_plain_text())

    while True:
        default_id = get_id(text + (str(count) if count > 0 else ''))

        if default_id in ids.keys():
            count += 1
        else:
            break

    ids[default_id] = heading

    if default_id not in heading.ids:
        heading.ids.append(default_id)


def build_content(ids: IDsMap, content: CContent):
    if isinstance(content, CHeading):
        build_heading(ids, content)

    for child in content.get_children():
        build_content(ids, child)


def validate_link(ids: IDsMap, link: CLinkText):
    if link.reference is not None:
        reference = link.reference
    else:
        reference = '\n'.join(link.get_plain_text())

    ref_id = get_id(reference)

    if ref_id not in ids.keys():
        raise Exception(f'Invalid reference: {reference}')

    link.reference = ref_id


def validate_content(ids: IDsMap, content: CContent):
    if isinstance(content, CLinkText):
        validate_link(ids, content)

    for child in content.get_children():
        validate_content(ids, child)
