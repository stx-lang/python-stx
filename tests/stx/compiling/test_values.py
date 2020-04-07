from typing import Any

from stx.compiling.reading.content import Content
from stx.data_notation.parsing import parse_value


def parse(text: str) -> Any:
    source = Content(text, 'test')

    return parse_value(source).to_any()


def test_parse_value():
    assert parse('~') is None
    assert parse('abc') == 'abc'
    assert parse('`abc`') == 'abc'
    assert parse('a:1') == {'a': '1'}
    assert parse('nothing:~') == {'nothing': None}
    assert parse('~, ~, ~') == [None, None, None]
    assert parse('a:1, b:2') == {'a': '1', 'b': '2'}
    assert parse('a:1, b:(2, 3, 4), c:5') == {
        'a': '1', 'b': ['2', '3', '4'], 'c': '5'}
