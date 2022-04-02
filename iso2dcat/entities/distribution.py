# -*- coding: utf-8 -*-
from rdflib import URIRef, RDF, Literal
from rdflib.namespace import DCTERMS
from urllib.parse import quote, urlparse
from iso2dcat.entities.resource import DcatResource
from iso2dcat.exceptions import EntityFailed
from iso2dcat.entities.base import DCAT

ACCESS = ".//gmd:transferOptions/*/gmd:onLine/gmd:CI_OnlineResource[not(gmd:function/*/@codeListValue = 'download')]"
DOWNLOAD = ".//gmd:transferOptions/*/gmd:onLine/gmd:CI_OnlineResource[gmd:function/*/@codeListValue = 'download']"

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

    def make_uri(self, accessURL):
        return self.sanitize_url(accessURL)

    def sanitize_url(self, url):
        parsed_url = urlparse(url.text)
        if '|' in parsed_url.query:
            out_url = parsed_url._replace(query=quote(parsed_url.query))
            return out_url.geturl()
        return url.text

    def add_distribution(self, title, accessURL, downloadURL=None):
        uri = self.make_uri(accessURL)
        self.rdf.add([URIRef(uri), RDF.type, self.entity_type])
        self.rdf.add([URIRef(uri), DCTERMS.title, Literal(title)])
        self.rdf.add((URIRef(uri), DCAT.accessURL, URIRef(self.sanitize_url(accessURL))))
        self.rdf.add([URIRef(self.parent), DCAT.distribution, URIRef(uri)])

        if downloadURL:
            self.rdf.add((URIRef(uri), DCAT.downloadURL, URIRef(self.sanitize_url(downloadURL))))

    def run(self):
        access_nodes = self.node.xpath(ACCESS, namespaces=self.nsm.namespaces)
        download_nodes = self.node.xpath(DOWNLOAD, namespaces=self.nsm.namespaces)
        if access_nodes :
            self.inc('dcat:accessURL')
        else:
            self.inc('no dcat:accessURL')
            if not download_nodes:
                self.inc('no dcat:accessURL')
                raise EntityFailed('No AccessURL for Distribution')

        if download_nodes :
             self.inc('dcat:downloadURL')

        for access_node in access_nodes:
            accessURL = access_node.xpath('gmd:linkage/*', namespaces =self.nsm.namespaces)
            title = access_node.xpath('gmd:description/gco:CharacterString[text()]', namespaces =self.nsm.namespaces)
            if len(title) == 0:
                title = 'Zugang'
            else:
                title = title[0]
            self.add_distribution(title, accessURL[0])

        for download_node in download_nodes:
            downloadURL = download_node.xpath('gmd:linkage/*', namespaces =self.nsm.namespaces)
            title = download_node.xpath('gmd:description/gco:CharacterString[text()]', namespaces =self.nsm.namespaces)
            if len(title) == 0:
                title = 'Download'
            else:
                title = title[0]
            self.add_distribution(title, downloadURL[0], downloadURL[0])

        return self.rdf
