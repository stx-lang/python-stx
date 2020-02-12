from typing import List, Optional

from stx.compiling.reading.chain import Chain
from stx.compiling.reading.content import Content
from stx.utils.thread_context import context


class Reader:

    def __init__(self):
        self._current_chain: Optional[Chain] = None
        self._chain_stack: List[Chain] = []

    def __enter__(self):
        context.push_reader(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        context.pop_reader()

    def push_file(self, file_path: str):
        self.push_files([file_path])

    def push_files(self, file_paths: List[str]):
        self._chain_stack.append(Chain(file_paths))
        self._current_chain = None

    def active(self) -> bool:
        if len(self._chain_stack) > 0:
            return True
        elif self._current_chain is not None:
            return self._current_chain.active()
        return False

    def get_chain(self) -> Chain:
        if self._current_chain is None:
            if len(self._chain_stack) == 0:
                raise Exception('no chain available')

            self._current_chain = self._chain_stack.pop()

        return self._current_chain

    def get_content(self) -> Content:
        chain = self.get_chain()
        content = chain.get_current_content()

        if content is None:
            if len(self._chain_stack) == 0:
                raise Exception('no more chains!')

            self._chain_stack.pop()

            chain = self.get_chain()
            content = chain.get_current_content()

        if content is None:
            raise Exception('no more content')

        return content
