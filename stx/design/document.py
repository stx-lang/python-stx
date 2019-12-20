from stx.design.attributes_map import AttributesMap


class Document:

    def __init__(self):
        self.content = None
        self.refs = None
        self.index = None
        self.links = AttributesMap()
