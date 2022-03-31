# -*- coding: utf-8 -*-
from rdflib import URIRef, RDF
from urllib.parse import quote
from iso2dcat.entities.resource import DcatResource
from iso2dcat.exceptions import EntityFailed
from iso2dcat.entities.base import DCAT

ACCESS_URL = ".//gmd:transferOptions/*/gmd:onLine/gmd:CI_OnlineResource[not(gmd:function/*/@codeListValue = 'download')]/gmd:linkage/*"
DOWNLOAD_URL = ".//gmd:transferOptions/*/gmd:onLine/gmd:CI_OnlineResource[gmd:function/*/@codeListValue = 'download']/gmd:linkage/*"

class Distribution(DcatResource):

    dcat_class = 'dcat_Distribution'
    entity_type = DCAT.Distribution
    dct_format = None
    dct_media_type = None
    dcat_accessURLs = None
    dcat_downloadURLs = None

    def add_entity_type(self):
        pass
        # self.rdf.add([URIRef(self.uri), RDF.type, self.entity_type])

    def base_uri(self):
        return None

    def make_uri(self, accessURL, downloadURL=None):
        if downloadURL is not None:
            return quote(downloadURL.text)
        else:
            return quote(accessURL.text)

    def run(self):
        accessURLs = self.node.xpath(ACCESS_URL, namespaces=self.nsm.namespaces)

        downloadURLs = self.node.xpath(DOWNLOAD_URL, namespaces=self.nsm.namespaces)

        if downloadURLs:
            self.inc('dcat:downloadURL')
        if not accessURLs:
            if not downloadURLs:
                self.inc('no dcat:accessURL')
                raise EntityFailed('dcat:Distribution incomplete: Missing accessURL')
            else:
                self.inc('dcat:downloadURL -> accessURL')

            accessURLs = downloadURLs
            downloadURLs = []
        else:
            self.inc('dcat:accessURL')

        for accessURL in accessURLs :
            if downloadURLs:
                uri = self.make_uri(accessURL, downloadURLs[0])
            else:
                uri = self.make_uri(accessURL, None)

            self.rdf.add([URIRef(uri), RDF.type, self.entity_type])
            self.rdf.add((URIRef(uri), DCAT.accessURL, URIRef(quote(accessURL.text))))
            self.rdf.add([URIRef(self.parent), DCAT.distribution, URIRef(uri)])

            if downloadURLs:
                self.rdf.add((URIRef(uri), DCAT.downloadURL, URIRef(quote(downloadURLs[0].text))))

        try:
            self.to_rdf4j(self.rdf)
        except Exception as e:
            a=10
        return self.rdf
