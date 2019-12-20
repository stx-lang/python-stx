from stx import logger
from stx.components import Component, Heading, LinkText
from stx.ref_map import make_ref, RefMap


def link_component(component: Component) -> RefMap:
    ref_map = RefMap()

    logger.info('Processing `ref` attributes...')
    consume_ref_attribute(ref_map, component)

    logger.info('Building automatic references...')
    build_content(ref_map, component)

    logger.info('Validating links references...')
    validate_content(ref_map, component)

    return ref_map


def consume_ref_attribute(ref_map: RefMap, component: Component):
    for child in component.walk():
        for ref in child.attributes.get_list('ref'):
            ref = make_ref(ref)

            ref_map.register_ref(ref, child)


def build_heading(ref_map: RefMap, heading: Heading):
    ref_map.register_content(heading, main=True)


def build_content(ref_map: RefMap, content: Component):
    if isinstance(content, Heading):
        build_heading(ref_map, content)

    for child in content.get_children():
        build_content(ref_map, child)


def validate_link(ref_map: RefMap, link: LinkText):
    if link.reference is not None and not link.internal:
        return

    if link.reference is not None:
        reference = link.reference
    else:
        reference = link.get_text()

    ref = make_ref(reference)

    if not ref_map.contains_ref(ref):
        print(f'WARNING: Invalid reference: {reference}')

    link.reference = ref


def validate_content(ref_map: RefMap, content: Component):
    for child in content.walk():
        if isinstance(child, LinkText):
            validate_link(ref_map, child)
