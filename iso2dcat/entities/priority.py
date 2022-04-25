from rdflib import URIRef, Literal

from iso2dcat.entities.base import BaseEntity
from iso2dcat.namespace import INQ


class InqbusPriority(BaseEntity):
    def __init__(self, node, rdf, parent_uri):
        super().__init__(node, rdf, parent_uri)
        self.parent_ressource_uri = parent_uri

    def run(self):
        try:
            priority = self.dcm.id_to_priority(self.uuid)
            self.inc('good')
        except KeyError:
            priority = self.cfg.DEFAULT_PRIORITY
            self.inc('bad')
        self.inc(str(priority))
        self.rdf.add((URIRef(self.parent_ressource_uri), INQ.priority, Literal(priority)))

        return self.rdf
