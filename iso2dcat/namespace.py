from rdflib import Graph
from rdflib.namespace import NamespaceManager, Namespace

from iso2dcat.component.interface import INamespaceManager
from zope import component
import zope

NAMESPACES = {
    'gmd': 'http://www.isotc211.org/2005/gmd',
    'csw': 'http://www.opengis.net/cat/csw/2.0.2',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'gco': 'http://www.isotc211.org/2005/gco',
    'gml': 'http://www.opengis.net/gml/3.2',
    'gmx': 'http://www.isotc211.org/2005/gmx',
    'gts': 'http://www.isotc211.org/2005/gts',
    'ogc': 'http://www.opengis.net/ogc',
    'ows': 'http://www.opengis.net/ows',
    'srv': 'http://www.isotc211.org/2005/srv',
    'dcatde': 'http://dcat-ap.de/def/dcatde/',
    'vcard': 'http://www.w3.org/2006/vcard/ns#',
    'adms': 'http://www.w3.org/ns/adms#',
    'locn': 'https://www.w3.org/ns/locn',
    'dct': 'http://purl.org/dc/terms/'
}

DCATDE = Namespace('http://dcat-ap.de/def/dcatde/')
LOCN = Namespace('https://www.w3.org/ns/locn')
DCAT = Namespace('http://www.w3.org/ns/dcat#')
ADMS = Namespace('http://www.w3.org/ns/adms#')
vcard = Namespace('http://www.w3.org/2006/vcard/ns#')
GSP = Namespace('http://www.opengis.net/ont/geosparql#')


@zope.interface.implementer(INamespaceManager)
class NsManager:

    def __init__(self):
        self.rdf = Graph()
        self.nsm = NamespaceManager(self.rdf)
        for prefix, ns in NAMESPACES.items():
            self.nsm.bind(prefix, ns)

    def uri2prefix_name(self, uri):
        prefix, _uri, name = self.nsm.compute_qname(uri)
        return prefix + '_' + name

    @property
    def namespaces(self):
        return NAMESPACES


def register_nsmanager():
    nsm = NsManager()
    component.provideUtility(nsm, INamespaceManager)
    return nsm
