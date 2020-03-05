from __future__ import annotations

import os
from typing import Dict, List, Optional

from gramat import actions
from gramat.expressions import Expression, EvalContext
from gramat.lexing.lexer import generate_nodes
from gramat.lexing.nodes import SyntaxNode
from gramat.parsing.source import Source


class GrammarReference:

    def __init__(self, gramat_file: str, rule_name: str):
        self.gramat_file = gramat_file
        self.rule_name = rule_name

    def tokenize(self, content: str) -> List[SyntaxNode]:
        gramat_file = self.gramat_file
        grammar = actions.compile_file(gramat_file)
        rule = grammar.get_rule(self.rule_name)

        source = Source(content)

        context = EvalContext(source)

        while source.position < source.length:
            pos0 = source.position

            rule.eval(context)

            if source.position == pos0:
                source.move_next()

        return generate_nodes(source, context.matches)


root = os.path.join(os.path.dirname(__file__), 'built_in')

_registry: Dict[str, GrammarReference] = {
    'stx': GrammarReference(os.path.join(root, 'stx.gmt'), 'stx'),
    'json': GrammarReference(os.path.join(root, 'json.gmt'), 'json'),
    'gramat': GrammarReference(os.path.join(root, 'gramat.gmt'), 'gramat'),
}


def register_grammar(lang: str, gramat_file: str, rule_name: str):
    _registry[lang] = GrammarReference(gramat_file, rule_name)


def get_grammar(lang: str) -> Optional[GrammarReference]:
    return _registry.get(lang)
