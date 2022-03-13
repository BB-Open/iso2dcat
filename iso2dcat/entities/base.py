from lxml import etree
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, FOAF, DCTERMS, Namespace
from zope import component

from iso2dcat.component.interface import IDCM, ICfg, ILogger, IStat, IRDFDatabase, INamespaceManager

DCAT = Namespace('http://www.w3.org/ns/dcat#')


class Base:
    """Base class of all instances. Gives access to logger, configuration and statistics"""

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

    def inc(self, stat, no_uuid=False):
        self.stat.inc(self, stat, no_uuid)


class BaseDCM(Base):
    """Base class of all instances using the DCM data"""

    _dcm = None
    _nsm = None
    _rdf4j = None

    @property
    def dcm(self):
        if self._dcm is None:
            self._dcm = component.queryUtility(IDCM)
        return self._dcm

    @property
    def rdf4j(self):
        if self._rdf4j is None:
            self._rdf4j = component.queryUtility(IRDFDatabase)
        return self._rdf4j

    @property
    def nsm(self):
        if self._nsm is None:
            self._nsm = component.queryUtility(INamespaceManager)
        return self._nsm

    def to_rdf4j(self, rdf):
        self.logger.info('Write Data to RDF4J store')
        rdf_ttl = rdf.serialize(format='turtle')
        self.rdf4j.insert_data(rdf_ttl, 'text/turtle')
        self.logger.info('Data written')


class BaseEntity(BaseDCM):
    """Base class of all entities."""

    data = None
    _uuid = None
    _base_uri = None
    _uri = None
    dcat_class = None
    entity_type = None

    def __init__(self, node):
        self.node = node
        self.rdf = Graph()

        for prefix, URI in self.nsm.nsm.namespaces():
            self.rdf.bind(prefix, URI)

        if self.entity_type is not None:
            self.add_entity_type()

    def add_entity_type(self):
        self.rdf.add([URIRef(self.uri), RDF.type, self.entity_type])

    @property
    def uuid(self):
        if self._uuid is None:
            self._uuid = self.node.fileIdentifier.getchildren()[0]
        return self._uuid

    @property
    def base_uri(self):
        if self._uuid is None:
            self._base_uri = self.dcm.file_id_to_baseurl(self.uuid)
        return self._base_uri

    @property
    def uri(self):
        if self._uri is None:
            self._uri = self.make_uri()
        return self._uri

    def make_uri(self):
        return self.base_uri + '#' + self.dcat_class + '_' + self.uuid

    def run(self):
        pass

    def __str__(self):
        etree.tostring(self.data, pretty_print=True)

