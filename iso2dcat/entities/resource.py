# -*- coding: utf-8 -*-
from pkan_config.namespaces import DCATDE, DCAT, ADMS
from pkan_config.namespaces import DCTERMS
from rdflib import Literal

from iso2dcat.entities.base import BaseEntity
from iso2dcat.entities.categories import CategoryKeywordMapper
from iso2dcat.entities.contactpoint import ContactPoint
from iso2dcat.entities.dates import DateMapper
from iso2dcat.entities.foafdocuments import FoafDocuments
from iso2dcat.entities.locationboundingbox import LocationBoundingbox
from iso2dcat.entities.periodicity import AccrualPeriodicity
from iso2dcat.entities.priority import InqbusPriority
from iso2dcat.entities.publisher import Publisher, Contributor, Maintainer
from iso2dcat.exceptions import EntityFailed

TITLE = './/gmd:identificationInfo[1]/*/gmd:citation/*/gmd:title/gco:CharacterString[text()]'
DESCRIPTION = './/gmd:identificationInfo[1]/*/gmd:abstract/gco:CharacterString[text()]'


class DcatResource(BaseEntity):

    def run(self):
        super(DcatResource, self).run()

        titles = self.node.xpath(TITLE, namespaces=self.nsm.namespaces)
        descriptions = self.node.xpath(DESCRIPTION, namespaces=self.nsm.namespaces)

        clean_languages = self.get_languages()

        if not titles or not descriptions:
            self.inc('Bad')
            self.inc('Bad Title and Description')
            raise EntityFailed('DcatRessource incomplete: Missing Title or Description')

        uri_ref = self.make_uri_ref(self.uri)

        for title in titles:
            for lang in clean_languages:
                self.add_tripel(uri_ref, DCTERMS.title, Literal(title, lang=lang))

        for description in descriptions:
            for lang in clean_languages:
                self.add_tripel(
                    uri_ref,
                    DCTERMS.description,
                    Literal(description, lang=lang)
                )

        publisher = Publisher(self.node, self.rdf)
        try:
            publisher.run()
        except EntityFailed:
            self.logger.warning('No publisher found')
        else:
            self.add_tripel(uri_ref, DCTERMS.publisher, self.make_uri_ref(publisher.uri))

        # Maintainer
        maintainer = Maintainer(self.node, self.rdf)
        if publisher.role == 'custodian':
            # do not create two identical foaf agents
            self.add_tripel(uri_ref, DCATDE.maintainer, self.make_uri_ref(publisher.uri))
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
                self.add_tripel(uri_ref, DCATDE.maintainer, self.make_uri_ref(maintainer.uri))

        contact = ContactPoint(self.node, self.rdf)
        try:
            rdf = contact.run()
        except EntityFailed:
            self.logger.warning('No Contact Point')
        else:
            self.add_tripel(uri_ref, DCAT.contactPoint, self.make_uri_ref(contact.uri))

        # catalog link
        # get base_uri without fallback to decide, if catalog suffix must be added
        base_uri = self.dcm.file_id_to_baseurl(self.uuid)

        catalog = base_uri + '#dcat_Catalog'

        self.add_tripel(self.make_uri_ref(catalog), DCAT.dataset, uri_ref)

        # contributorID
        self.add_tripel(
            uri_ref,
            DCATDE.contributorID,
            self.make_uri_ref('http://dcat-ap.de/def/contributors/landBrandenburg')
        )
        # identifier is uuid
        self.add_tripel(uri_ref, DCTERMS.identifier, Literal(self.uuid))
        self.add_tripel(uri_ref, ADMS.identifier, Literal(self.uuid))

        # contributor
        contributor = Contributor(self.node, self.rdf)
        try:
            rdf = contributor.run()
        except EntityFailed:
            self.logger.warning('No Contributor found')
        else:
            self.add_tripel(uri_ref, DCTERMS.contributor, self.make_uri_ref(contributor.uri))

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
            self.add_tripel(uri_ref, DCTERMS.spatial, self.make_uri_ref(spatial.uri))

        # dct:accrualPeriodicity
        periodicity = AccrualPeriodicity(self.node, self.rdf, self.uri)
        rdf = periodicity.run()

        # foaf:homepage
        page = FoafDocuments(self.node, self.rdf, self.uri)
        rdf = page.run()

        # inq:priority
        priority = InqbusPriority(self.node, self.rdf, self.uri)
        rdf = priority.run()
