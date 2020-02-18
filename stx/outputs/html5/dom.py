from __future__ import annotations

from typing import Any, Dict, TextIO, List, Optional

from stx.outputs.html5.escaping import write_text


class Element:

    def render(self, out: TextIO):
        raise NotImplementedError()


class Text(Element):

    def __init__(self, content: str):
        self.content = content

    def render(self, out: TextIO):
        if self.content is not None:
            write_text(self.content, out)


class Literal(Element):

    def __init__(self, content: str):
        self.content = content

    def render(self, out: TextIO):
        out.write(self.content)


class Tag(Element):

    def __init__(
            self,
            name: str,
            children: List[Element] = None,
            attributes: Dict[str, Any] = None):
        self.name = name
        self.preserve_spaces = False
        self._children: Optional[List[Element]] = children
        self._attributes: Optional[Dict[str, Any]] = attributes

    def __getitem__(self, key: str) -> Any:
        return self.attributes[key]

    def __setitem__(self, key: str, value: Any):
        self.attributes[key] = value

    def append_tag(
            self,
            name: str,
            attributes: Dict[str, Any] = None,
            *args,
            text: str = None) -> Tag:

        if text is not None:
            children = [Text(text)]
        else:
            children = None

        tag = Tag(name, attributes=attributes, children=children)
        self.children.append(tag)
        return tag

    def append_text(self, value: str) -> Text:
        element = Text(value)
        self.children.append(element)
        return element

    def append_literal(self, value: str) -> Literal:
        element = Literal(value)
        self.children.append(element)
        return element

    @property
    def attributes(self) -> Dict[str, Any]:
        if self._attributes is None:
            self._attributes = {}
        return self._attributes

    @property
    def children(self) -> List[Element]:
        if self._children is None:
            self._children = []
        return self._children

    def render(self, out: TextIO):
        out.write('<')
        out.write(self.name)

        if self._attributes is not None and len(self._attributes) > 0:
            out.write(' ')

            for index, (key, value) in enumerate(self._attributes.items()):
                if index > 0:
                    out.write(' ')
                out.write(key)

                if value is not None:
                    out.write('=')
                    out.write('"')
                    write_text(value, out)
                    out.write('"')

        out.write('>')

        if self._children is not None and len(self._children) > 0:
            for child in self._children:
                child.render(out)

            out.write('</')
            out.write(self.name)
            out.write('>')
