# -*- coding: utf-8 -*-
import zope
from rdflib import URIRef, Literal
from rdflib.namespace import FOAF, RDF, DCTERMS

from iso2dcat.component.interface import ICatalog
from iso2dcat.entities.base import BaseEntity
from iso2dcat.namespace import DCAT, ADMS


@zope.interface.implementer(ICatalog)
class Catalog(BaseEntity):

    _stat_title = 'The catalogs created'
    _stat_desc = 'Each detail line shows the name of the catalog created'
    _stat_uuid = False
    _stat_count = True
    catalog = {}

    def run(self):
        self.logger.info('Create Fallback Catalog')
        self.create(self.cfg.FALLBACK_CATALOG_NAME, self.cfg.FALLBACK_URL)

        if self.dcm.dcm is None:
            self.logger.info('No DCM not creating Catalog')
            return
        publishers = self.dcm.dcm['publisher']['mapping']

        for pub in publishers:
            name = pub['publisher_name']
            self.logger.info('Working on ' + name)
            base_url = pub['publisher_url']
            self.create(name, base_url)

    def create(self, name, base_url):
        self.inc('Processed')
        self.inc(name)
        foaf_agent_url = base_url + '#foaf_Agent'
        catalog_url = base_url + '#dcat_Catalog'
        self.logger.info('Create Publisher')
        uri_pub = URIRef(foaf_agent_url)
        self.rdf.add((uri_pub, RDF.type, FOAF.Agent))
        self.rdf.add((uri_pub, FOAF.name, Literal(name, lang='de')))
        self.logger.info('Publisher Created')
        self.logger.info('Create Catalog')
        uri_cat = URIRef(catalog_url)
        self.rdf.add((uri_cat, RDF.type, DCAT.Catalog))
        self.rdf.add((uri_cat, DCTERMS.title, Literal(name, lang='de')))
        self.rdf.add((uri_cat, DCTERMS.publisher, uri_pub))
        self.rdf.add((uri_cat, DCTERMS.description, Literal(name, lang='de')))
        self.rdf.add((URIRef(uri_cat), ADMS.identifier, Literal(uri_cat)))
        self.rdf.add((URIRef(uri_cat), DCTERMS.identifier, Literal(uri_cat)))
        self.rdf.add(
            (uri_cat, DCAT.themeTaxonomy, URIRef('http://publications.europa.eu/resource/authority/data-theme/')))
        self.logger.info('Catalog Created')
        self.inc('Good')

        # identifier = self.node.fileIdentifier.getchildren()[0].text
        # if identifier in self.dcm.dcm:
        #     key = self.dcm.dcm[identifier]['publisher']
        #     self.inc('good')
        # else:
        #     self.inc('bad')
