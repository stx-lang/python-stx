import threading


class _ThreadContext:

    def __init__(self):
        self._local = threading.local()

    @property
    def reader(self):
        stack = self._get_reader_stack()

        if len(stack) == 0:
            return None

        return stack[-1]

    def _get_reader_stack(self):
        stack = getattr(self._local, 'reader_stack', None)

        if stack is None:
            stack = []
            setattr(self._local, 'reader_stack', stack)

        return stack

    def push_reader(self, source):
        self._get_reader_stack().append(source)

    def pop_reader(self):
        self._get_reader_stack().pop()


context = _ThreadContext()
