from stx.compiling.source import Source
from stx.compiling.values import parse_value


def parse(text: str) -> str:
    source = Source(text, 'test')

    return parse_value(source)


def test_parse_value():
    assert parse('abc') == 'abc'
    assert parse('"abc"') == 'abc'
    assert parse('{}') == {}
    assert parse('{a:b,c:d}') == {'a': 'b', 'c': 'd'}
    assert parse('[a,b,c]') == ['a', 'b', 'c']
