import tempfile

from stx.app import process_file

STX_CONTENT = '''
- Item
  +++

  +++
'''


def test_issue_3():
    with tempfile.NamedTemporaryFile() as file:
        with open(file.name, mode='w') as w:
            w.write(STX_CONTENT)

        process_file(file.name)
