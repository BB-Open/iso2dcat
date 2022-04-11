from rdflib import URIRef, Literal
from rdflib.namespace import RDF, DCTERMS, RDFS

from iso2dcat.entities.base import BaseEntity
from iso2dcat.exceptions import EntityFailed

QUERY = './/gmd:resourceConstraints/*/gmd:otherConstraints/gmx:Anchor'


class RightsStatement(BaseEntity):
    dcat_class = 'dct_RightsStatement'

    def run(self):
        values = self.node.xpath(QUERY, namespaces=self.nsm.namespaces)
        if values:
            self.inc('good')
        else:
            self.inc('bad')
            raise EntityFailed
        statement = values[0]
        self.rdf.add((URIRef(self.uri), RDF.type, DCTERMS.RightsStatement))
        for lang in self.get_languages():
            self.rdf.add((URIRef(self.uri), RDFS.label, Literal(statement, lang=lang)))
