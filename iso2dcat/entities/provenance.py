import hashlib

from iso2dcat.entities.base import BaseEntity
from iso2dcat.exceptions import EntityFailed
from rdflib import URIRef, Literal
from rdflib.namespace import RDF, DCTERMS, RDFS

QUERY = ".//gmd:dataQualityInfo/*/gmd:lineage/*/gmd:statement/gco:CharacterString"


class ProvenanceStatement(BaseEntity):
    _stat_title = 'ProvenanceStatement'
    _stat_desc = """ProvenanceStatements are quite important for OpenData. They describe the origin of the data.
This field is not mandatory, but it is important.
"""

    dcat_class = 'dct_ProvenanceStatement'

    @property
    def uri(self):
        return self._uri

    def run(self):
        self.inc('Processed')
        values = self.node.xpath(QUERY, namespaces=self.nsm.namespaces)
        if values:
            self.inc('Good')
        else:
            self.inc('Bad')
            raise EntityFailed
        statement = values[0]
        hash_statement = hashlib.md5(str(statement).encode()).hexdigest()
        self._uri = self.base_uri + '#' + self.dcat_class + '_' + hash_statement
        self.add_tripel(URIRef(self.uri), RDF.type, DCTERMS.ProvenanceStatement)
        for lang in self.get_languages():
            self.add_tripel(URIRef(self.uri), RDFS.label, Literal(statement, lang=lang))
