# -*- coding: utf-8 -*-
from urllib.parse import quote, urlparse

from rdflib import URIRef, RDF, Literal
from rdflib.namespace import DCTERMS

from iso2dcat.entities.dates import DateMapper
from iso2dcat.entities.licenses import License
from iso2dcat.entities.provenance import ProvenanceStatement
from iso2dcat.entities.resource import DcatResource
from iso2dcat.entities.rightstatement import RightsStatement
from iso2dcat.exceptions import EntityFailed
from iso2dcat.namespace import DCAT

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
        for lang in self.languages:
            self.rdf.add([URIRef(uri), DCTERMS.title, Literal(title, lang=lang)])
        self.rdf.add((URIRef(uri), DCAT.accessURL, URIRef(self.sanitize_url(accessURL))))
        self.rdf.add([URIRef(self.parent), DCAT.distribution, URIRef(uri)])

        if downloadURL is not None:
            self.rdf.add((URIRef(uri), DCAT.downloadURL, URIRef(self.sanitize_url(downloadURL))))

        licenses = License(self.node, self.rdf, uri)
        rdf = licenses.run()

        if self.rightstatement:
            self.rdf.add((URIRef(uri), DCTERMS.accessRights, URIRef(self.rightstatement.uri)))
        if self.provenance:
            self.rdf.add((URIRef(uri), DCTERMS.provenance, URIRef(self.provenance.uri)))

    def run(self):
        self.languages = self.get_languages()
        self.rightstatement = RightsStatement(self.node, self.rdf)
        self.provenance = ProvenanceStatement(self.node, self.rdf)
        try:
            self.provenance.run()
        except EntityFailed:
            self.provenance = None

        try:
            self.rightstatement.run()
        except EntityFailed:
            self.rightstatement = None

        access_nodes = self.node.xpath(ACCESS, namespaces=self.nsm.namespaces)
        download_nodes = self.node.xpath(DOWNLOAD, namespaces=self.nsm.namespaces)

        if access_nodes:
            self.inc('dcat:accessURL')
        else:
            self.inc('no dcat:accessURL')
            if not download_nodes:
                self.inc('no dcat:accessURL')
                raise EntityFailed('No AccessURL for Distribution')

        if download_nodes:
            self.inc('dcat:downloadURL')

        for access_node in access_nodes:
            accessURL = access_node.xpath('gmd:linkage/*', namespaces=self.nsm.namespaces)
            title = access_node.xpath('gmd:description/gco:CharacterString[text()]', namespaces=self.nsm.namespaces)
            if len(title) == 0:
                title = 'Zugang: ' + accessURL[0]
            else:
                title = title[0]
            self.add_distribution(title, accessURL[0])

        for download_node in download_nodes:
            downloadURL = download_node.xpath('gmd:linkage/*', namespaces=self.nsm.namespaces)
            title = download_node.xpath('gmd:description/gco:CharacterString[text()]', namespaces=self.nsm.namespaces)
            if len(title) == 0:
                title = 'Download: ' + downloadURL[0]
            else:
                title = title[0]
            self.add_distribution(title, downloadURL[0], downloadURL=downloadURL[0])
