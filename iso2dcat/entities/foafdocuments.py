from urllib.parse import urlparse, quote

from rdflib import URIRef
from rdflib.namespace import FOAF

from iso2dcat.entities.base import BaseEntity
from iso2dcat.namespace import DCAT

QUERY_LANDING_PAGE = './/gmd:transferOptions/*/gmd:onLine/gmd:CI_OnlineResource[not(gmd:function/*/@codeListValue)]'
QUERY_FOAF_PAGE = ".//gmd:transferOptions/*/gmd:onLine/gmd:CI_OnlineResource[gmd:function/*/@codeListValue = 'information' or gmd:function/*/@codeListValue = 'search']"


class FoafDocuments(BaseEntity):

    dcat_class = 'foaf_document'

    def __init__(self, node, rdf, parent_uri):
        super().__init__(node, rdf)
        self.parent_ressource_uri = parent_uri

    def sanitize_url(self, url):
        parsed_url = urlparse(url.text)
        if '|' in parsed_url.query:
            out_url = parsed_url._replace(query=quote(parsed_url.query))
            return out_url.geturl()
        return url.text

    def run(self):
        values_landing = self.node.xpath(QUERY_LANDING_PAGE, namespaces=self.nsm.namespaces)
        if not values_landing:
            self.inc('bad landing page')
            self.logger.warning('No Landingpage found')
        else:
            self.inc('good landing page')

        for value in values_landing:
            links = value.xpath('gmd:linkage/*', namespaces=self.nsm.namespaces)
            self.logger.debug('Found Landing Page {values}'.format(values=links))
            for link in links:
                self.rdf.add((URIRef(self.parent_ressource_uri), DCAT.landingPage, URIRef(self.sanitize_url(link))))

        values_foaf_page = self.node.xpath(QUERY_FOAF_PAGE, namespaces=self.nsm.namespaces)
        if not values_foaf_page:
            self.inc('bad foaf page')
            self.logger.warning('No FOAF:Page found')
        else:
            self.inc('good foaf page')

        for value in values_foaf_page:
            links = value.xpath('gmd:linkage/*', namespaces=self.nsm.namespaces)
            self.logger.debug('Found FOAF Page {values}'.format(values=links))
            for link in links:
                self.rdf.add((URIRef(self.parent_ressource_uri), FOAF.page, URIRef(self.sanitize_url(link))))
