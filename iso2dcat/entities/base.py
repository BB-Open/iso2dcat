from lxml import etree
from rdflib import Graph
from zope import component

from iso2dcat.component.interface import IDCM, ICfg, ILogger, IStat
from iso2dcat.exceptions import EntityFailed


class Base:
    """Base class of all instances. Gains access to logger and configuration"""

    _stat = None

    @property
    def logger(self):
        return component.queryUtility(ILogger)

    @property
    def cfg(self):
        return component.queryUtility(ICfg)

    @property
    def stat(self):
        if self._stat is None:
            self._stat = component.queryUtility(IStat)
        return self._stat


class BaseDCM(Base):
    """Base class of all instances using the DCM data"""

    @property
    def dcm(self):
        return component.queryUtility(IDCM)

    def inc(self, stat, no_uuid=False):
        self.stat.inc(self, stat, no_uuid)


class BaseEntity(BaseDCM):
    """Base class of all entities."""

    data = None
    namespaces = None

    def __init__(self, node):
        self.node = node
        self.rdf = Graph()
        if self.namespaces is not None:
            for namespace, URI in self.namespaces.items():
                self.rdf.bind(namespace, URI)

    @property
    def uuid(self):
        return self.node.fileIdentifier.getchildren()[0]

    def run(self):
        pass


    def __str__(self):
        etree.tostring(self.data, pretty_print=True)
