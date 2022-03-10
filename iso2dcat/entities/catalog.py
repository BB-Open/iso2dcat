# -*- coding: utf-8 -*-
from rdflib import FOAF, URIRef, RDF, Literal

from iso2dcat.component.interface import IStat, ICatalog
from iso2dcat.entities.base import BaseEntity
import zope


@zope.interface.implementer(ICatalog)
class Catalog(BaseEntity):

    catalog = {}
    namespaces = {
        'foaf': FOAF
    }

    def run(self):
        publishers  = self.dcm.dcm['publisher']['mapping']
        print(publishers)

        for pub in publishers:
            name = pub['publisher_name']
            self.logger.info('Working on ' + name)
            base_url = pub['publisher_url']
            foaf_agent_url = base_url + '#foafagent'
            catalog_url = base_url + '#catalog'
            self.logger.info('Create Publisher')
            uri_pub = URIRef(foaf_agent_url)
            self.rdf.add((uri_pub, RDF.type, FOAF.Agent))
            self.rdf.add((uri_pub, FOAF.name, Literal(name, lang='de')))

        return self.rdf

        # identifier = self.node.fileIdentifier.getchildren()[0].text
        # if identifier in self.dcm.dcm:
        #     key = self.dcm.dcm[identifier]['publisher']
        #     self.inc('good')
        # else:
        #     self.inc('bad')
