
from lxml import etree
from rdflib import URIRef, ConjunctiveGraph
from rdflib.namespace import RDF
from zope import component

from iso2dcat.component.interface import \
    IDCM, \
    ILogger, \
    IStat, \
    IRDFDatabase, \
    INamespaceManager, \
    ILanguageMapper, \
    IIsoCfg
from iso2dcat.exceptions import EntityFailed

LANGUAGE = './/gmd:language/*/@codeListValue'

INVALID_URI_CHARS = '<>" {}|\\^`[]'

class Base:
    """Base class of all instances. Gives access to logger, configuration and statistics"""

    _stat = None

    @property
    def logger(self):
        return component.queryUtility(ILogger)

    @property
    def cfg(self):
        return component.queryUtility(IIsoCfg)


class BaseStat(Base):

    _stat_title = "Base statistics"
    _stat_desc = "The base statistics show a histogram of different aspects of the entity"
    _stat_count = True
    _stat_uuid = True

    def __init__(self):
        if self.stat:
            self.stat.init(self)

    @property
    def stat(self):
        if self._stat is None:
            self._stat = component.queryUtility(IStat)
        return self._stat

    def inc(self, stat, increment=1, no_uuid=False):
        self.stat.inc(self, stat, increment=increment, no_uuid=no_uuid)


def check_invalid_uri_chars(uri):
    for c in INVALID_URI_CHARS:
        if c in uri:
            return c
    return None


class BaseDCM(BaseStat):
    """Base class of all instances using the DCM data"""

    _dcm = None
    _nsm = None
    _rdf4j = None
    _language_mapper = None

    @property
    def dcm(self):
        if self._dcm is None:
            self._dcm = component.queryUtility(IDCM)
        return self._dcm

    @property
    def language_mapper(self):
        if self._language_mapper is None:
            self._language_mapper = component.queryUtility(ILanguageMapper)
        return self._language_mapper

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

    def make_uri_ref(self, uri):
        invalid_char = check_invalid_uri_chars(str(uri))
        if invalid_char:
            message = f'Invalid Char "{invalid_char}"'
            self.inc(message)
            self.logger.error(message)
            raise EntityFailed(message)
        else:
            return URIRef(uri)


class BaseEntity(BaseDCM):
    """Base class of all entities."""

    data = None
    _uuid = None
    _base_uri = None
    _uri = None
    _languages = {}
    dcat_class = None
    entity_type = None

    def __init__(self, node, rdf=None, parent=None):
        super(BaseEntity, self).__init__()
        self.node = node
        self.parent = parent
        if rdf is None:
            rdf = ConjunctiveGraph()
        self.rdf = rdf

    def add_tripel(self, s, p, o):
        self.rdf.addN([(s, p, o, self.uuid.text)])

    def set_namespaces(self):
        for prefix, URI in self.nsm.nsm.namespaces():
            self.rdf.bind(prefix, URI)

    def get_languages(self):
        if self.uuid in self._languages:
            self.logger.debug('Use cached Languages')
            return self._languages[self.uuid]
        languages = self.node.xpath(LANGUAGE, namespaces=self.nsm.namespaces)
        if not languages:
            # untagged
            languages = ['']
        clean_languages = self.language_mapper.convert(languages, self)
        self._languages[self.uuid] = clean_languages
        return clean_languages

    def add_entity_type(self):
        if self.entity_type:
            self.add_tripel(self.make_uri_ref(self.uri), RDF.type, self.entity_type)

    @property
    def uuid(self):
        if self._uuid is None:
            self._uuid = self.node.fileIdentifier.getchildren()[0]
        return self._uuid

    @property
    def base_uri(self):
        if self._base_uri is None:
            self._base_uri = self.dcm.file_id_to_baseurl(self.uuid)
        return self._base_uri

    @property
    def uri(self):
        if self._uri is None:
            self._uri = self.make_uri()
        return self._uri

    def make_uri(self):
        if self.dcat_class:
            return self.base_uri + '#' + self.dcat_class + '_' + self.uuid
        else:
            self.logger.error('Missing self.dcat_class')
            return self.base_uri + '#' + self.uuid

    def run(self):
        pass

    def __str__(self):
        etree.tostring(self.data, pretty_print=True)
