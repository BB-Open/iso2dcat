import hashlib

from rdflib import URIRef, Literal
from rdflib.namespace import RDF, DCTERMS, RDFS

from iso2dcat.entities.base import BaseEntity
from iso2dcat.exceptions import EntityFailed

QUERY = './/gmd:resourceConstraints/*/gmd:otherConstraints/gmx:Anchor'


class RightsStatement(BaseEntity):
    _stat_title = 'RightsStatement'
    _stat_desc = """RightsStatement are quite important for OpenData. They describe the way the data can be used ander the given License.
This field is not mandatory, but it is important.
    """

    dcat_class = 'dct_RightsStatement'

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
        self.add_tripel(URIRef(self.uri), RDF.type, DCTERMS.RightsStatement)
        for lang in self.get_languages():
            self.add_tripel(URIRef(self.uri), RDFS.label, Literal(statement, lang=lang))
