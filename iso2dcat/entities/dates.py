from rdflib import Literal, URIRef
from rdflib.namespace import DCTERMS, XSD

from iso2dcat.entities.base import BaseEntity

DATE_QUERY= "gmd:identificationInfo[1]/*/gmd:citation/*/gmd:date/*[gmd:dateType/*/@codeListValue=$role]/gmd:date/*"


class DateMapper(BaseEntity):
    cached_keywords = {}

    def __init__(self, node, parent_uri):
        super().__init__(node)
        self.parent_ressource_uri = parent_uri
        self.roles = ['revision', 'creation', 'publication']

    def run(self):
        # modified
        roles = ['creation', 'revision']
        results = None
        for role in roles:
            results = self.node.xpath(DATE_QUERY, role=role,
                                      namespaces=self.nsm.namespaces)
            if results:
                break

        if results:
            self.inc('modified_good')
            self.rdf.add((URIRef(self.parent_ressource_uri), DCTERMS.modified, Literal(results[0])))
        else:
            self.inc('modified_bad')

        # issued
        roles = ['revision', 'publication']
        results = None
        for role in roles:
            results = self.node.xpath(DATE_QUERY, role=role,
                                      namespaces=self.nsm.namespaces)
            if results:
                break

        if results:
            self.inc('issued_good')
            self.rdf.add((URIRef(self.parent_ressource_uri), DCTERMS.issued, Literal(results[0], datatype=XSD.dateTimeStamp)))
        else:
            self.inc('issued_bad')

        return self.rdf
