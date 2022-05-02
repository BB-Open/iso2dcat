from rdflib import URIRef, Literal

from iso2dcat.entities.base import BaseEntity
from iso2dcat.namespace import INQ


class InqbusPriority(BaseEntity):
    _stat_title = 'Inqbus:Priority'
    _stat_desc = """This field is nether an ISO nor a DCAT related field.
Its purpose is to prioritize datasets of certain providers (currently only LGB) in te SOLR search.
In details the distribution of priorities is shown"""

    def __init__(self, node, rdf, parent_uri):
        super().__init__(node, rdf, parent_uri)
        self.parent_ressource_uri = parent_uri

    def run(self):
        self.inc('Processed')
        try:
            priority = self.dcm.id_to_priority(self.uuid)
            self.inc('Good')
        except KeyError:
            priority = self.cfg.DEFAULT_PRIORITY
            self.inc('Bad')
        self.inc(str(priority))
        self.add_tripel(URIRef(self.parent_ressource_uri), INQ.priority, Literal(priority))

        return self.rdf
