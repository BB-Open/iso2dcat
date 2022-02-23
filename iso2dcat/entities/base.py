from lxml import etree
from zope import component

from iso2dcat.component.interface import ILogger, ICfg
from iso2dcat.exceptions import EntityFailed


class Base:

    @property
    def logger(self):
        return component.queryUtility(ILogger)

    @property
    def cfg(self):
        return component.queryUtility(ICfg)


class BaseEntity(Base):

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