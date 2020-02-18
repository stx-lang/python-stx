from typing import List, Optional

from stx.compiling.reading.chain import Chain
from stx.compiling.reading.content import Content
from stx.compiling.reading.location import Location
from stx.utils.thread_context import context


class Reader:

    def __init__(self):
        self._chain_stack: List[Chain] = []

    def push_file(self, file_path: str):
        self.push_files([file_path])

    def push_files(self, file_paths: List[str]):
        self._chain_stack.append(Chain(file_paths))

    def active(self) -> bool:
        chain = self.get_chain()

        return chain is not None and chain.active()

    def get_chain(self) -> Optional[Chain]:
        while True:
            if len(self._chain_stack) == 0:
                return None

            chain = self._chain_stack[-1]

            if chain.active():
                return chain

            self._chain_stack.pop()

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

    def get_location(self) -> Optional[Location]:
        if not self.active():
            return None

        return self.get_content().get_location()
