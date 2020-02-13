from typing import List

from stx.components import Component, TableOfContents, ElementReference, \
    Section, Composite
from stx.document import Document


# TODO implement index of tables and figures


def link_document_tocs(document: Document):
    if document.content is not None:
        link_component_tocs(document, document.content)


def link_component_tocs(document: Document, root: Component):
    for component in root.walk():
        if isinstance(component, TableOfContents):
            link_table_of_contents(document, component)


def link_table_of_contents(document: Document, toc: TableOfContents):
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
