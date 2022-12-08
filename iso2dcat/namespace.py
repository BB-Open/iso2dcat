import zope
from pkan_config.namespaces import NAMESPACES
from rdflib import Graph
from rdflib.namespace import NamespaceManager
from zope import component

from iso2dcat.component.interface import INamespaceManager


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


def unregister_nsmanager():
    component.provideUtility(None, INamespaceManager)
