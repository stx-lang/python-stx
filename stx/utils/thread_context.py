import threading


class _ThreadContext:

    def __init__(self):
        self.local = threading.local()

    @property
    def source_stack(self):
        stack = getattr(self.local, 'source_stack', None)

        if stack is None:
            stack = []
            setattr(self.local, 'source_stack', stack)

        return stack

    @property
    def source(self):
        stack = self.source_stack

        if len(stack) == 0:
            return None

        return stack[-1]

    def push_source(self, source):
        self.source_stack.append(source)

    def pop_source(self):
        self.source_stack.pop()


context = _ThreadContext()
