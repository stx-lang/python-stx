# from stx.compiling.parsing.paragraph import parse_contents, Tape
# from stx.compiling.reading.content import Content
# from stx.rendering.json.serializer import components_to_json
#
#
# def check(actual: str, stop: str, expected):
#     assert components_to_json(parse_contents(Content(actual), stop)) == expected
#
#
# def test_parse_contents():
#     check('abc', '', [
#         {
#             'type': 'plain-text',
#             'content': 'abc'
#         },
#     ])
#     check('a*b*c', '', [
#         {
#             'type': 'plain-text',
#             'content': 'a'
#         },
#         {
#             'type': 'styled-text',
#             'style': 'strong',
#             'contents': [{
#                 'type': 'plain-text',
#                 'content': 'b'
#             }],
#         },
#         {
#             'type': 'plain-text',
#             'content': 'c'
#         },
#     ])
