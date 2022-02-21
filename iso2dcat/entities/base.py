from lxml import etree

from iso2dcat.error import EntityFailed


class Base:

    good = None
    bad = None
    data = None

    def __init__(self, node):
        self.node = node

    def run(self):
        pass

    def get_entity(self):
        try:
            res = self.run()
            self.good += 1
        except EntityFailed as e:
            self.bad += 1
            raise(e)

        return res

    def __str__(self):
        etree.tostring(self.data, pretty_print=True)