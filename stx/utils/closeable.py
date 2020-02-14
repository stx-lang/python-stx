from typing import Callable, Any


class Closeable:

    def __init__(
            self,
            enter_action: Callable[[], Any],
            exit_action: Callable[[], Any]):
        self.enter_action = enter_action
        self.exit_action = exit_action

    def __enter__(self):
        self.enter_action()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            raise exc_val

        self.exit_action()
