# -*- coding: utf-8 -*-
from rdflib import URIRef, Literal
from rdflib.namespace import DCTERMS
from iso2dcat.entities.base import DCAT

from iso2dcat.entities.base import BaseEntity
from iso2dcat.entities.contactpoint import ContactPoint
from iso2dcat.entities.publisher import Publisher

TITLE = './/gmd:identificationInfo[1]/*/gmd:citation/*/gmd:title/gco:CharacterString[text()]'
DESCRIPTION = './/gmd:identificationInfo[1]/*/gmd:abstract/gco:CharacterString[text()]'


class DcatResource(BaseEntity):

    def run(self):
        super(DcatResource, self).run()

        titles = self.node.xpath(TITLE, namespaces=self.nsm.namespaces)
        descriptions = self.node.xpath(DESCRIPTION, namespaces=self.nsm.namespaces)

        for title in titles:
            self.rdf.add((URIRef(self.uri), DCTERMS.title, Literal(title)))

        for description in descriptions:
            self.rdf.add((URIRef(self.uri), DCTERMS.description, Literal(description)))

#        publisher = Publisher(self.node)
#        rdf = publisher.run()
#        self.rdf += rdf
#        self.rdf.add([URIRef(self.uri), DCTERMS.publisher, URIRef(publisher.uri)])

        contact = ContactPoint(self.node)
        rdf = contact.run()
        self.rdf += rdf
        self.rdf.add([URIRef(self.uri), DCAT.contactPoint, URIRef(contact.uri)])

        # catalog link
        catalog = self.base_uri + '#dcat_Catalog'
        self.rdf.add([URIRef(catalog), DCAT.dataset, URIRef(self.uri)])

        return self.rdf
