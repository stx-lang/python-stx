import pytest

from stx.reader import Reader, ETX


def test_indentation_recognition():
    reader = Reader('  abc\n   def\n    ghi\n123\n 456\n  789\n')

    assert reader.read_chars(2) == '  '

    reader.push_indent(2)

    assert reader.read_chars(4) == 'abc\n'
    assert reader.read_chars(5) == ' def\n'
    assert reader.read_chars(6) == '  ghi\n'
    assert reader.read_chars(1) is None

    reader.push_indent(0)

    assert reader.read_chars(4) == '123\n'
    assert reader.read_chars(5) == ' 456\n'
    assert reader.read_chars(6) == '  789\n'
    assert reader.read_chars(1) is None


def test_transactions():
    reader = Reader('123456789000')

    reader.begin_position()  # transaction A

    assert reader.read_chars(3) == '123'

    reader.begin_position()  # transaction B

    assert reader.read_chars(3) == '456'

    reader.begin_position()  # transaction C

    assert reader.read_chars(3) == '789'

    reader.rollback_position()  # rollback C

    assert reader.read_chars(3) == '789'

    reader.commit_position()  # commit B

    assert reader.read_chars(3) == '000'

    reader.rollback_position()  # rollback A

    assert reader.read_chars(3) == '123'


def test_tests():
    reader = Reader('123')

    assert reader.test('1') is True
    assert reader.test('12') is True
    assert reader.test('123') is True

    assert reader.test('1234') is False
    assert reader.test('abc') is False
    assert reader.test('') is False


def test_expects():
    reader = Reader('123abc')

    with pytest.raises(Exception):
        reader.expect('1234')

    reader.expect('123')
    reader.expect('abc')


def test_continuation_on_empty_lines():
    reader = Reader('  abc1\n \n  abc2\n\nabc3')

    assert reader.read_chars(2) == '  '

    reader.push_indent(2)

    assert reader.read_chars(4) == 'abc1'
    assert reader.read_char() == ETX
    assert reader.read_chars(4) == 'abc2'
    assert reader.read_char() is None

    reader.pop_indent()

    assert reader.read_chars(4) == 'abc3'
    assert reader.read_char() is None
