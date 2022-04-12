import hashlib

from rdflib import URIRef, Literal
from rdflib.namespace import RDF, DCTERMS, RDFS

from iso2dcat.entities.base import BaseEntity
from iso2dcat.exceptions import EntityFailed

QUERY = './/gmd:resourceConstraints/*/gmd:otherConstraints/gmx:Anchor'


class RightsStatement(BaseEntity):
    dcat_class = 'dct_RightsStatement'

    @property
    def uri(self):
        return self._uri

    def run(self):
        values = self.node.xpath(QUERY, namespaces=self.nsm.namespaces)
        if values:
            self.inc('good')
        else:
            self.inc('bad')
            raise EntityFailed
        statement = values[0]
        hash_statement = hashlib.md5(str(statement).encode()).hexdigest()
        self._uri = self.base_uri + '#' + self.dcat_class + '_' + hash_statement
        self.rdf.add((URIRef(self.uri), RDF.type, DCTERMS.RightsStatement))
        for lang in self.get_languages():
            self.rdf.add((URIRef(self.uri), RDFS.label, Literal(statement, lang=lang)))
