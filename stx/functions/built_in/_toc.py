from stx.functions import utils
from stx.components import FunctionCall
from typing import List

from stx.components import Component, TableOfContents, ElementReference, \
    Section, Composite
from stx.document import Document


# TODO implement index of tables and figures


def resolve_toc(document: Document, call: FunctionCall) -> Component:
    options = utils.make_options_dict(call, key_for_str='title')

    title = options.pop('title')

    utils.check_unknown_options(options, call)

    toc = TableOfContents(call.location, title)

    generate_toc(document, toc)

    return toc


def generate_toc(document: Document, toc: TableOfContents):
    if document.content is not None:
        collect_section_toc(document.content, toc.elements)


def collect_section_toc(
        component: Component, elements: List[ElementReference]):
    if isinstance(component, Section):
        element = ElementReference(
            title=component.heading.get_text().strip(),
            reference=component.get_main_ref(),
            number=component.number,
        )

        elements.append(element)

        collect_section_toc(component.content, element.elements)
    elif isinstance(component, Composite):
        for child in component.components:
            collect_section_toc(child, elements)
