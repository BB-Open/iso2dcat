# -*- coding: utf-8 -*-
from rdflib import URIRef, Literal
from rdflib.namespace import DCTERMS

from iso2dcat.entities.base import BaseEntity
from iso2dcat.entities.categories import CategoryKeywordMapper
from iso2dcat.entities.contactpoint import ContactPoint
from iso2dcat.entities.dates import DateMapper
from iso2dcat.entities.foafdocuments import FoafDocuments
from iso2dcat.entities.locationboundingbox import LocationBoundingbox
from iso2dcat.entities.periodicity import AccrualPeriodicity
from iso2dcat.entities.publisher import Publisher, Contributor, Maintainer
from iso2dcat.exceptions import EntityFailed
from iso2dcat.namespace import DCATDE, DCAT, ADMS, INQ

TITLE = './/gmd:identificationInfo[1]/*/gmd:citation/*/gmd:title/gco:CharacterString[text()]'
DESCRIPTION = './/gmd:identificationInfo[1]/*/gmd:abstract/gco:CharacterString[text()]'


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

        publisher = Publisher(self.node, self.rdf)
        try:
            publisher.run()
        except EntityFailed:
            self.logger.warning('No publisher found')
        else:

            self.rdf.add([URIRef(self.uri), DCTERMS.publisher, URIRef(publisher.uri)])

        # Maintainer
        maintainer = Maintainer(self.node, self.rdf)
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
                self.rdf.add([URIRef(self.uri), DCATDE.maintainer, URIRef(maintainer.uri)])

        contact = ContactPoint(self.node, self.rdf)
        try:
            rdf = contact.run()
        except EntityFailed:
            self.logger.warning('No Contact Point')
        else:
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
        self.rdf.add(
            (URIRef(self.uri), DCATDE.contributorID, URIRef('http://dcat-ap.de/def/contributors/landBrandenburg')))
        # identifier is uuid
        self.rdf.add((URIRef(self.uri), DCTERMS.identifier, Literal(self.uuid)))
        self.rdf.add((URIRef(self.uri), ADMS.identifier, Literal(self.uuid)))

        # contributor
        contributor = Contributor(self.node, self.rdf)
        try:
            rdf = contributor.run()
        except EntityFailed:
            self.logger.warning('No Contributor found')
        else:
            self.rdf.add([URIRef(self.uri), DCTERMS.contributor, URIRef(contributor.uri)])

        # categories
        categories = CategoryKeywordMapper(self.node, self.rdf, self.uri)
        try:
            rdf = categories.run()
        except EntityFailed:
            self.logger.warning('No Keywords or Categories found')

        # issued/modified
        dates = DateMapper(self.node, self.rdf, self.uri)
        try:
            rdf = dates.run()
        except EntityFailed:
            self.logger.warning('No Dates found')

        # dct:spatial
        spatial = LocationBoundingbox(self.node, self.rdf)
        try:
            rdf = spatial.run()
        except EntityFailed:
            self.logger.warning('No Bounding Box found')
        else:
            self.rdf.add((URIRef(self.uri), DCTERMS.spatial, URIRef(spatial.uri)))

        # dct:accrualPeriodicity
        periodicity = AccrualPeriodicity(self.node, self.rdf, self.uri)
        rdf = periodicity.run()

        # foaf:homepage
        page = FoafDocuments(self.node, self.rdf, self.uri)
        rdf = page.run()

        # inq:priority
        priority = self.dcm.id_to_priority(self.uuid)
        self.rdf.add((URIRef(self.uri), INQ.priority, Literal(priority)))
