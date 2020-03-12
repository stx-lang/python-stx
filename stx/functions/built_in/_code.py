from typing import List

from gramat.errors import GramatError
from gramat.lexing.nodes import SyntaxNode, ContainerNode, TokenNode

from stx.compiling.reading.location import Location
from stx.functions import utils
from stx.components import FunctionCall, Component, CodeBlock, \
    PlainText, CustomText
from stx.document import Document
from stx.grammars import registry


def generate_component(
        location: Location,
        nodes: List[SyntaxNode],
        components: List[Component]):
    for node in nodes:
        if node.rule is not None:
            wrapper = CustomText(location, [], node.rule)

            target = wrapper.contents

            components.append(wrapper)
        else:
            target = components

        if isinstance(node, TokenNode):
            target.append(PlainText(location, node.token))
        elif isinstance(node, ContainerNode):
            generate_component(location, node.nodes, target)
        else:
            raise GramatError(f'unknown node: {node}')


def resolve_code(document: Document, call: FunctionCall) -> Component:
    if call.argument is None:
        raise call.error('Code function requires a captured component.')

    options = utils.make_options_dict(call, key_for_str='lang')

    lang = options.pop('lang', None)

    utils.check_unknown_options(options, call)

    contents = None

    if lang is not None:
        grammar = registry.get_grammar(lang)

        if grammar is not None:
            text = utils.make_plain_text(call.argument)

            try:
                contents = []
                nodes = grammar.tokenize(text)
                generate_component(call.location, nodes, contents)
            except GramatError:
                contents = None

    if contents is None:
        contents = utils.make_component_list(call.argument)

    return CodeBlock(call.location, contents, lang=lang)
