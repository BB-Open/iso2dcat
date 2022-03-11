from lxml import etree
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, FOAF, DCTERMS, Namespace
from zope import component

from iso2dcat.component.interface import IDCM, ICfg, ILogger, IStat

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
    namespaces = {
        'gmd': 'http://www.isotc211.org/2005/gmd',
        'csw' : 'http://www.opengis.net/cat/csw/2.0.2',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'gco': 'http://www.isotc211.org/2005/gco',
        'gml': 'http://www.opengis.net/gml/3.2',
        'gmx': 'http://www.isotc211.org/2005/gmx',
        'gts': 'http://www.isotc211.org/2005/gts',
        'ogc': 'http://www.opengis.net/ogc',
        'ows': 'http://www.opengis.net/ows',
        'srv': 'http://www.isotc211.org/2005/srv',
        'dcat': str(DCAT._NS),
        'dcatde': 'http://dcat-ap.de/def/dcatde/',
        'foaf': str(FOAF._NS),
        'dct': str(DCTERMS._NS),
    }
    _uuid = None
    _base_uri = None
    _uri = None
    dcat_class = None
    entity_type = None

    def __init__(self, node):
        self.node = node
        self.rdf = Graph()
        if self.namespaces is not None:
            for namespace, URI in self.namespaces.items():
                self.rdf.bind(namespace, URI)

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
