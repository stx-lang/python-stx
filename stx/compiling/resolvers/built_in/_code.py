from typing import List

from gramat.errors import GramatError
from gramat.lexing.nodes import SyntaxNode, ContainerNode, TokenNode

from stx.compiling.reading.location import Location
from stx.compiling.resolvers import utils
from stx.components import FunctionCall, Component, Literal, CodeBlock, \
    PlainText, Composite, CustomText
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
    text = utils.make_literal_arg(call)

    options = utils.make_options_dict(call, key_for_str='lang')

    lang = options.pop('lang', None)

    utils.check_unknown_options(options, call)

    grammar = registry.get_grammar(lang)

    contents = []

    if grammar is not None:
        try:
            nodes = grammar.tokenize(text)

            generate_component(call.location, nodes, contents)
        except GramatError:
            pass

    if len(contents) == 0:
        contents.append(
            PlainText(call.location, text)
        )

    return CodeBlock(call.location, contents, lang=lang)
