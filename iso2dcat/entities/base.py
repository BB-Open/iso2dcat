from lxml import etree
from rdflib import Graph
from zope import component

from iso2dcat.component.interface import IDCM, ICfg, ILogger
from iso2dcat.exceptions import EntityFailed


class Base:
    """Base class of all instances. Gains access to logger and configuration"""

    @property
    def logger(self):
        return component.queryUtility(ILogger)

    @property
    def cfg(self):
        return component.queryUtility(ICfg)


class BaseDCM(Base):
    """Base class of all instances using the DCM data"""

    @property
    def dcm(self):
        return component.queryUtility(IDCM)


class BaseEntity(BaseDCM):
    """Base class of all entities."""

    good = 0
    bad = 0
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

    @classmethod
    def show_stats(cls):
        print('{}: good:{} bad:{}'.format(cls.__name__, cls.good, cls.bad))

    def __str__(self):
        etree.tostring(self.data, pretty_print=True)
