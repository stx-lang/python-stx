import string
from typing import Set, Optional

from stx import logger
from stx.components import Component, Section, Table, Figure, LinkText
from stx.document import Document
from stx.utils.debug import see

REF_LENGTH_HINT = 40


# TODO refactor `ref` attribute, auto-generation,
#  normalization and validation.


def auto_generate_special_references(document: Document):
    roots = list()
    refs = set()

    if document.content is not None:
        roots.append(document.content)

    for root in roots:
        normalize_references(root)

    for root in roots:
        collect_references(root, refs)

    for root in roots:
        register_missing_references(root, refs)


def validate_references(document: Document):
    roots = list()
    refs = set()

    if document.content is not None:
        roots.append(document.content)

    for root in roots:
        collect_references(root, refs)

    for root in roots:
        normalize_and_report_invalid_links(root, refs)


def collect_references(root: Component, refs: Set[str]):
    for component in root.walk():
        for ref in component.get_refs():
            if ref in refs:
                raise component.error(f'Reference already taken: {ref}')
            else:
                refs.add(ref)


def normalize_references(root: Component):
    for component in root.walk():
        wild_refs = component.get_refs()

        if len(wild_refs) > 0:
            component.ref = [
                make_ref(wild_ref) for wild_ref in wild_refs
            ]


def register_missing_references(root: Component, refs: Set[str]):
    for component in root.walk():
        if not component.has_refs():
            if isinstance(component, Section):
                register_section_reference(component, refs)
            elif isinstance(component, Table):
                register_table_reference(component, refs)
            elif isinstance(component, Figure):
                register_figure_reference(component, refs)


def normalize_and_report_invalid_links(root: Component, refs: Set[str]):
    for component in root.walk():
        if isinstance(component, LinkText):
            if component.reference is None:
                # Generate reference from the text
                component.reference = make_ref(component.get_text())
            elif component.is_internal():
                # Normalize wild reference
                component.reference = make_ref(component.reference)
            else:
                # Do not validate this link
                continue

            if component.reference not in refs:
                component.invalid = True
                logger.warning(
                    f'Invalid link: {see(component.reference, None)}',
                    component.location)


def register_section_reference(section: Section, refs: Set[str]):
    ref = generate_component_ref(section.heading, refs)

    section.add_ref(ref)
    refs.add(ref)


def register_table_reference(table: Table, refs: Set[str]):
    if table.caption is not None:
        ref = generate_component_ref(table.caption, refs)
    else:
        ref = generate_component_ref(table, refs)

    table.add_ref(ref)
    refs.add(ref)


def register_figure_reference(figure: Figure, refs: Set[str]):
    ref = generate_component_ref(figure.caption, refs)

    figure.add_ref(ref)
    refs.add(ref)


def generate_component_ref(component: Component, refs: Set[str]) -> str:
    count = 0

    plain_text = component.get_text()

    while True:
        ref = make_ref(plain_text, REF_LENGTH_HINT, count)

        if ref not in refs:
            break

        count += 1

    return ref


def make_ref(
        base: str,
        length_hint: Optional[int] = None,
        count: Optional[int] = None) -> str:
    result = []

    # Important generate it in lowercase and trimmed
    for c in base.strip().lower():
        if c in string.ascii_lowercase or c in string.digits:
            result.append(c)
        elif length_hint is not None and len(result) >= length_hint:
            break
        elif len(result) == 0 or result[-1] != '-':
            result.append('-')

    ref = ''.join(result)

    if count is not None and count > 0:
        if ref.endswith('-'):
            ref += str(count)
        else:
            ref += f'-{count}'

    return ref
