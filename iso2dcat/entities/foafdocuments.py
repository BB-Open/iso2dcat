from urllib.parse import urlparse, quote


from pkan_config.namespaces import FOAF, RDF, DCAT

from iso2dcat.entities.base import BaseEntity
from iso2dcat.exceptions import EntityFailed

QUERY_LANDING_PAGE = './/gmd:transferOptions/*/gmd:onLine/gmd:CI_OnlineResource' \
    '[not(gmd:function/*/@codeListValue)]'
QUERY_FOAF_PAGE = ".//gmd:transferOptions/*/gmd:onLine/gmd:CI_OnlineResource" \
    "[gmd:function/*/@codeListValue = 'information' or gmd:function/*/@codeListValue = 'search']"


class FoafDocuments(BaseEntity):
    dcat_class = 'foaf_document'

    _stat_title = 'foaf:Document'
    _stat_desc = """Convert gmd:CI_OnlineResource[not(gmd:function/*/@codeListValue)]
    to dcat:landingPage
Convert gmd:CI_OnlineResource
    [gmd:function/*/@codeListValue = 'information' or gmd:function/*/@codeListValue = 'search']
    to foaf:Page
"""

    def __init__(self, node, rdf, parent_uri):
        super().__init__(node, rdf)
        self.parent_ressource_uri = parent_uri

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
                try:
                    target = self.make_uri_ref(link)
                    parent = self.make_uri_ref(self.parent_ressource_uri)
                except EntityFailed:
                    # do not add with invalid chars
                    continue
                self.add_tripel(
                    parent,
                    DCAT.landingPage,
                    target
                )
                self.add_tripel(target, RDF.type, FOAF.Document)

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
                try:
                    target = self.make_uri_ref(link)
                    parent = self.make_uri_ref(self.parent_ressource_uri)
                except EntityFailed:
                    # do not add with invalid chars
                    continue
                self.add_tripel(
                    parent,
                    FOAF.page,
                    target
                )
                self.add_tripel(target, RDF.type, FOAF.Document)

        if values_foaf_page or values_landing:
            self.inc('Good')
        else:
            self.inc('Bad')
        self.inc('Processed')
