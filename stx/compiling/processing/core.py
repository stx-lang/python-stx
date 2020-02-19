from stx.compiling.processing import registry
from stx.components import Component, MacroText
from stx.document import Document
from stx.utils.stx_error import StxError
from stx.utils.debug import see


def process_document_macros(document: Document):
    if document.content is not None:
        for component in document.content.walk():
            if isinstance(component, MacroText):
                process_macro(document, component)


def process_macro(document: Document, macro: MacroText):
    macro_key = macro.entry.name
    macro_value = macro.entry.value

    processor = registry.get_macro(macro_key)

    if processor is None:
        raise StxError(
            f'Macro not supported: {see(macro_key)}', macro.location)

    macro.content = processor(document, macro.location, macro_value)
