from lxml import etree
from rdflib import Graph
from zope import component

from iso2dcat.component.interface import IDCM, ICfg, ILogger
from iso2dcat.exceptions import EntityFailed


class Base:

    @property
    def logger(self):
        return component.queryUtility(ILogger)

    @property
    def cfg(self):
        return component.queryUtility(ICfg)


class BaseDCM(Base):

    @property
    def dcm(self):
        return component.queryUtility(IDCM)


class BaseEntity(BaseDCM):

    good = None
    bad = None
    data = None

    namespaces = None

    def __init__(self, node):
        self.node = node
        self.rdf = Graph()
        if self.namespaces is not None:
            for namespace, URI in self.namespaces.items():
                self.rdf.bind(namespace, URI)

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
