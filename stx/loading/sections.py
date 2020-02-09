from typing import List

from stx.components import Component, Heading, Section, Composite, \
    Separator

SECTIONS = ['sect1', 'sect2', 'sect3', 'sect4', 'sect5']


def make_sections(component: Component) -> Component:
    result = []
    section_stack = []

    make_sections_loop(result, section_stack, component)

    if len(result) == 1:
        return result[0]

    for item in result:
        if isinstance(item, Section):
            if item.type is None:
                item.type = 'chapter'

            apply_sections(item)

    return Composite(result)


def apply_sections(section: Section, index=0):
    for item in section.components:
        if isinstance(item, Section) and item.type is None:
            item.type = SECTIONS[index]

            if index < len(SECTIONS):
                apply_sections(item, index + 1)


def add_component(result: List[Component], section_stack: List[Section], component: Component):
    if len(section_stack) == 0:
        result.append(component)
    else:
        section_stack[-1].components.append(component)


def normalize_level(section_stack: List[Section], section: Section):
    while len(section_stack) > 0:
        if section.heading.level <= section_stack[-1].heading.level:
            section_stack.pop()
        else:
            break


def make_sections_loop(result: List[Component], section_stack: List[Section], component: Component) -> List[Component]:
    if isinstance(component, Composite):
        for component in component.components:
            if isinstance(component, Heading):
                section = Section(component, [], None)

                normalize_level(section_stack, section)

                add_component(result, section_stack, section)

                section_stack.append(section)
            elif isinstance(component, Separator):
                for i in range(component.level):
                    if len(section_stack) > 0:
                        section_stack.pop()
            else:
                make_sections_loop(result, section_stack, component)
    else:
        add_component(result, section_stack, component)

    return result
