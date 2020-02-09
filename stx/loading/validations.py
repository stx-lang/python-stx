from stx.components import Component
from stx.design.document import Document


def validate_attributes(document: Document):
    if document.header is not None:
        validate_walking(document.header)

    validate_walking(document.content)

    if document.footer is not None:
        validate_walking(document.footer)


def validate_walking(component: Component):
    for child in component.walk():
        for attribute_key in child.attributes.get_unread_attributes():
            print(f'Unread attribute: {attribute_key}')
