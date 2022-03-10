# -*- coding: utf-8 -*-
from rdflib import URIRef, DCTERMS, Literal, DCAT

from iso2dcat.entities.base import BaseEntity
from iso2dcat.entities.contactpoint import ContactPoint
from iso2dcat.entities.publisher import Publisher

TITLE = './/gmd:identificationInfo[1]/*/gmd:citation/*/gmd:title/gco:CharacterString[text()]'
DESCRIPTION = './/gmd:identificationInfo[1]/*/gmd:abstract/gco:CharacterString[text()]'


class DcatResource(BaseEntity):

    def run(self):
        super(DcatResource, self).run()

        title = self.node.xpath(TITLE, namespaces=self.namespaces)
        description = self.node.xpath(DESCRIPTION, namespaces=self.namespaces)

        if title is not None:
            try:
                self.rdf.add((URIRef(self.uri), DCTERMS.title, Literal(title)))
            except Exception:
                pass
        if description is not None:
            try:
                self.rdf.add((URIRef(self.uri), DCTERMS.description, Literal(description)))
            except Exception:
                pass

#        publisher = Publisher(self.node)
#        rdf = publisher.run()
#        self.rdf += rdf
#        self.rdf.add([URIRef(self.uri), DCTERMS.publisher, URIRef(publisher.uri)])

        contact = ContactPoint(self.node)
        rdf = contact.run()
        self.rdf += rdf
        self.rdf.add([URIRef(self.uri), DCAT.contactPoint, URIRef(contact.uri)])

        return self.rdf
