from typing import List


class HtmlTheme:

    def __init__(self):
        self.head_styles: List[str] = []
        self.head_scripts: List[str] = []
        self.body_scripts: List[str] = []


class NullHtmlTheme(HtmlTheme):

    pass
