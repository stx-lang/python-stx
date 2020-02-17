from stx import logger
from stx.components import Component, Composite, Section, Table, Figure
from stx.document import Document

# TODO implement numbers for section type


def link_document_numbers(document: Document):
    if document.content is not None:
        link_section_numbers(document.content, '', 1)
        link_figure_and_table_numbers(document.content)


def link_section_numbers(
        root: Component, parent_number: str, current_level: int):
    if isinstance(root, Composite):
        count = 1
        for child in root.components:
            if isinstance(child, Section):
                child.number = parent_number + f'{count}.'

                if child.level != current_level:
                    logger.warning(
                        f'Expected section level {current_level}'
                        f' instead of {child.level}.',
                        child.location)

                link_section_numbers(
                    child.content, child.number, current_level + 1)

                count += 1
            else:
                link_section_numbers(child, parent_number, current_level)
    elif isinstance(root, Section):
        root.number = parent_number + '1.'

        link_section_numbers(root.content, root.number, current_level + 1)


def link_figure_and_table_numbers(root: Component):
    figure_count = 1
    table_count = 1

    for component in root.walk():
        if isinstance(component, Table):
            component.number = f'{table_count}.'

            table_count += 1
        elif isinstance(component, Figure):
            component.number = f'{figure_count}.'

            figure_count += 1
