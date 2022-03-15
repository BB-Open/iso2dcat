# -*- coding: utf-8 -*-
from rdflib import URIRef, Literal
from rdflib.namespace import DCTERMS, Namespace
from iso2dcat.entities.base import DCAT, ADMS

from iso2dcat.entities.base import BaseEntity
from iso2dcat.entities.contactpoint import ContactPoint
from iso2dcat.entities.publisher import Publisher, Contributor, Maintainer
from iso2dcat.exceptions import EntityFailed

TITLE = './/gmd:identificationInfo[1]/*/gmd:citation/*/gmd:title/gco:CharacterString[text()]'
DESCRIPTION = './/gmd:identificationInfo[1]/*/gmd:abstract/gco:CharacterString[text()]'

DCATDE = Namespace('http://dcat-ap.de/def/dcatde/')


class DcatResource(BaseEntity):

    def run(self):
        super(DcatResource, self).run()

        titles = self.node.xpath(TITLE, namespaces=self.nsm.namespaces)
        descriptions = self.node.xpath(DESCRIPTION, namespaces=self.nsm.namespaces)

        clean_languages = self.get_languages()

        if not titles or not descriptions:
            raise EntityFailed('DcatRessource incomplete: Missing Title or Description')
        # todo languages
        for title in titles:
            for lang in clean_languages:
                self.rdf.add((URIRef(self.uri), DCTERMS.title, Literal(title, lang=lang)))

        # todo languages
        for description in descriptions:
            for lang in clean_languages:
                self.rdf.add((URIRef(self.uri), DCTERMS.description, Literal(description, lang=lang)))

        publisher = Publisher(self.node)
        try:
            rdf = publisher.run()
        except EntityFailed:
            self.logger.warning('No publisher found')
        else:
            self.rdf += rdf
            self.rdf.add([URIRef(self.uri), DCTERMS.publisher, URIRef(publisher.uri)])

        # Maintainer
        maintainer = Maintainer(self.node)
        if publisher.role == 'custodian':
            # do not create two identical foaf agents
            self.rdf.add([URIRef(self.uri), DCATDE.maintainer, URIRef(publisher.uri)])
            maintainer.inc('good')
            maintainer.inc('reused_publisher')
            self.logger.info('Reused Publisher as Maintainer, cause same role custodian')
        else:
            self.logger.info('Create new Maintainer')
            try:
                rdf = maintainer.run()
            except EntityFailed:
                self.logger.warning('No Maintainer found')
            else:
                self.rdf += rdf
                self.rdf.add([URIRef(self.uri), DCATDE.maintainer, URIRef(maintainer.uri)])

        contact = ContactPoint(self.node)
        rdf = contact.run()
        self.rdf += rdf
        self.rdf.add([URIRef(self.uri), DCAT.contactPoint, URIRef(contact.uri)])

        # catalog link
        # get base_uri without fallback to decide, if catalog suffix must be added
        base_uri = self.dcm.file_id_to_baseurl(self.uuid, return_fallback=False)
        if base_uri:
            catalog = base_uri + '#dcat_Catalog'
        else:
            catalog = self.cfg.FALLBACK_CATALOG_URL
        self.rdf.add([URIRef(catalog), DCAT.dataset, URIRef(self.uri)])

        # contributorID
        self.rdf.add((URIRef(self.uri), DCATDE.contributorID, URIRef('http://dcat-ap.de/def/contributors/landBrandenburg')))
        # identifier
        self.rdf.add((URIRef(self.uri), DCTERMS.identifier, Literal(self.uri)))
        self.rdf.add((URIRef(self.uri), ADMS.identifier, Literal(self.uri)))

        # contributor
        contributor = Contributor(self.node)
        try:
            rdf = contributor.run()
        except EntityFailed:
            self.logger.warning('No Contributor found')
        else:
            self.rdf += rdf
            self.rdf.add([URIRef(self.uri), DCTERMS.contributor, URIRef(contributor.uri)])

        return self.rdf
