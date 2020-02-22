import threading


class _ThreadContext:

    def __init__(self):
        self._local = threading.local()

    @property
    def parser(self):
        stack = self._get_parser_stack()

        if len(stack) == 0:
            return None

        return stack[-1]

    def _get_parser_stack(self):
        stack = getattr(self._local, 'parser_stack', None)

        if stack is None:
            stack = []
            setattr(self._local, 'parser_stack', stack)

        return stack

    def push_reader(self, reader):
        self._get_parser_stack().append(reader)

    def pop_reader(self):
        self._get_parser_stack().pop()


context = _ThreadContext()
