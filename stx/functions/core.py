from stx.functions import registry
from stx.components import Component, FunctionCall
from stx.document import Document
from stx.utils.stx_error import StxError
from stx.utils.debug import see


def resolve_document(document: Document) -> int:
    count = 0

    if document.content is not None:
        count += resolve_component(document, document.content)

    return count


def resolve_component(document: Document, component: Component) -> int:
    count = 0
    children = component.get_children()

    # Resolve children first
    for child in children:
        count += resolve_component(document, child)

    # Resolve function then
    if isinstance(component, FunctionCall):
        count += resolve_function_call(document, component)

    return count


def resolve_function_call(document: Document, call: FunctionCall):
    # Check if it is already resolved
    if call.result is not None:
        return 0

    processor = registry.get(call.key)

    if processor is None:
        raise StxError(
            f'Function not found: {see(call.key)}', call.location)

    call.result = processor(document, call)

    if call.result is None:
        raise call.error('Function call did not produce a component.')

    return 1 + resolve_component(document, call.result)
