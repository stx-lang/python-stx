from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')


class Stack(Generic[T]):

    def __init__(self):
        self.items: List[T] = []

    def push(self, item: T):
        self.items.append(item)

    def pop(self) -> T:
        return self.items.pop()

    def peek(self) -> Optional[T]:
        if len(self.items) > 0:
            return self.items[-1]

        return None
