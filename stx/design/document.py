from stx.design.attributes_map import AttributesMap


class Document:

    def __init__(self):
        self.title = None
        self.author = None
        self.header = None
        self.content = None
        self.footer = None
        self.format = None
        self.encoding = None
        self.refs = None
        self.index = None
        self.links = AttributesMap()
