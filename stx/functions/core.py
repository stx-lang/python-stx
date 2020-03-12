from stx.functions import registry
from stx.components import Component, FunctionCall
from stx.document import Document
from stx.utils.stx_error import StxError
from stx.utils.debug import see


def resolve_document(document: Document):
    if document.content is not None:
        resolve_component(document, document.content)


def resolve_component(document: Document, component: Component):
    children = component.get_children()

    # Resolve children first
    for child in children:
        resolve_component(document, child)

    # Resolve function then
    if isinstance(component, FunctionCall):
        resolve_function_call(document, component)


def resolve_function_call(document: Document, call: FunctionCall):
    processor = registry.get(call.key)

    if processor is None:
        raise StxError(
            f'Function not found: {see(call.key)}', call.location)

    call.result = processor(document, call)

    if call.result is None:
        raise call.error('Function call did not produce a component.')

    resolve_component(document, call.result)
