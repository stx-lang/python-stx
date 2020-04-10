from __future__ import annotations

from typing import Dict, List, Optional

from gramat.compiling.compiler import compile_source
from gramat.expressions import EvalContext
from gramat.grammar import Grammar
from gramat.lexing.lexer import generate_nodes
from gramat.lexing.nodes import SyntaxNode
from gramat.options import Options
from gramat.parsing.source import Source
from gramat.actions import compile_file

from stx import resources, logger


def load_grammar(res_path: str) -> Grammar:
    code = resources.get_text(res_path)
    source = Source(code, src=res_path)
    return compile_source(source, Options())


class GrammarReference:

    def __init__(self, grammar: Grammar, rule_name: str):
        self.grammar = grammar
        self.rule_name = rule_name

    def tokenize(self, content: str) -> List[SyntaxNode]:
        rule = self.grammar.get_rule(self.rule_name)

        source = Source(content)

        context = EvalContext(source)

        while source.position < source.length:
            pos0 = source.position

            rule.eval(context)

            if source.position == pos0:
                source.move_next()

        return generate_nodes(source, context.matches)


_registry: Dict[str, GrammarReference] = {
    'stx': GrammarReference(load_grammar('grammars/stx.gmt'), 'stx'),
    'json': GrammarReference(load_grammar('grammars/json.gmt'), 'json'),
    'gramat': GrammarReference(load_grammar('grammars/gramat.gmt'), 'gramat'),
}


def register_grammar(lang: str, grammar: Grammar, rule_name: str):
    _registry[lang] = GrammarReference(grammar, rule_name)

    logger.info(f'Registered grammar for {lang} lang.')


def register_grammar_from_file(lang: str, gramat_file: str, rule_name: str):
    grammar = compile_file(gramat_file)

    register_grammar(lang, grammar, rule_name)


def get_grammar(lang: str) -> Optional[GrammarReference]:
    return _registry.get(lang)
