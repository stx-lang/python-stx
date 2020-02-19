from typing import List, Optional

from stx.compiling.reading.content import Content


class Chain:

    def __init__(self, file_paths: List[str]):
        self.file_paths = file_paths
        self._current_content: Optional[Content] = None

        if len(file_paths) == 0:
            raise Exception('no files available')

    def active(self) -> bool:
        content = self.get_current_content()

        return content is not None and not content.halted()

    def load_next_content(self) -> Optional[Content]:
        if len(self.file_paths) == 0:
            return None
        file_path = self.file_paths.pop(0)
        content = Content.from_file(file_path)
        return content

    def get_current_content(self) -> Optional[Content]:
        if self._current_content is None or self._current_content.halted():
            self._current_content = self.load_next_content()
        return self._current_content
