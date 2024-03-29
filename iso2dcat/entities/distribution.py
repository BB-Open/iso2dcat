# -*- coding: utf-8 -*-
from pkan_config.namespaces import DCAT, DCTERMS
from rdflib import RDF, Literal

from iso2dcat.entities.licenses import License
from iso2dcat.entities.provenance import ProvenanceStatement
from iso2dcat.entities.resource import DcatResource
from iso2dcat.entities.rightstatement import RightsStatement
from iso2dcat.exceptions import EntityFailed

ACCESS = ".//gmd:transferOptions/*/gmd:onLine/gmd:CI_OnlineResource" \
         "[not(gmd:function/*/@codeListValue = 'download')]"
DOWNLOAD = ".//gmd:transferOptions/*/gmd:onLine/gmd:CI_OnlineResource" \
           "[gmd:function/*/@codeListValue = 'download']"


class Distribution(DcatResource):

    _stat_title = 'dcat:Distribution'
    _stat_desc = """For each distribution an accessURL is mandatory.
If no accessURL is found the downloadURL is used as accessURL.
If no accessURL can be constructed this is a DCAT violation.
dcat:accessURL: number of AccessURLs found
dcat:downloadURL: number of DownloadURLs found
no dcat:accessURL: number of Distributions with no URL at all
no dcat:accessURL and no dcat:downloadURL: number of Files with missing distribution"""

    dcat_class = 'dcat_Distribution'
    entity_type = DCAT.Distribution
    dct_format = None
    dct_media_type = None
    dcat_accessURLs = None
    dcat_downloadURLs = None

    def add_entity_type(self):
        pass
        # self.add_tripel([self.make_uri_ref(self.uri), RDF.type, self.entity_type])

    def base_uri(self):
        return None

    def make_uri(self, accessURL):
        return accessURL

    def add_distribution(self, title, accessURL, downloadURL=None):
        if not accessURL and not downloadURL:
            self.logger.warning('No Url provided')
            raise EntityFailed('No Url provided')
        uri = self.make_uri(accessURL)
        uri_ref = self.make_uri_ref(uri)
        accessURL_ref = self.make_uri_ref(accessURL)
        if downloadURL:
            downloadURL_ref = self.make_uri_ref(downloadURL)
        else:
            downloadURL_ref = None
        self.add_tripel(uri_ref, RDF.type, self.entity_type)
        for lang in self.languages:
            self.add_tripel(uri_ref, DCTERMS.title, Literal(title, lang=lang))
        self.add_tripel(uri_ref, DCAT.accessURL, accessURL_ref)
        self.add_tripel(self.make_uri_ref(self.parent), DCAT.distribution, uri_ref)

        if downloadURL_ref:
            self.add_tripel(uri_ref, DCAT.downloadURL, downloadURL_ref)

        licenses = License(self.node, self.rdf, uri)
        rdf = licenses.run()

        if self.rightstatement:
            self.add_tripel(uri_ref, DCTERMS.accessRights, self.make_uri_ref(self.rightstatement.uri))
        if self.provenance:
            self.add_tripel(uri_ref, DCTERMS.provenance, self.make_uri_ref(self.provenance.uri))

    def run(self):
        self.inc('Processed')
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
                self.inc('no dcat:accessURL and no dcat:downloadURL')
                self.inc('Bad')
                raise EntityFailed('No AccessURL for Distribution')

        if download_nodes:
            self.inc('dcat:downloadURL')

        dist_counter = 0

        for access_node in access_nodes:
            accessURL = access_node.xpath('gmd:linkage/*', namespaces=self.nsm.namespaces)
            title = access_node.xpath(
                'gmd:description/gco:CharacterString[text()]',
                namespaces=self.nsm.namespaces
            )
            if len(title) == 0:
                title = 'Zugang: ' + accessURL[0]
            else:
                title = title[0]
            try:
                self.add_distribution(title, accessURL[0])
                dist_counter += 1
            except EntityFailed:
                pass

        for download_node in download_nodes:
            downloadURL = download_node.xpath('gmd:linkage/*', namespaces=self.nsm.namespaces)
            title = download_node.xpath(
                'gmd:description/gco:CharacterString[text()]',
                namespaces=self.nsm.namespaces
            )
            if len(title) == 0:
                title = 'Download: ' + downloadURL[0]
            else:
                title = title[0]
            try:
                self.add_distribution(title, downloadURL[0], downloadURL=downloadURL[0])
                dist_counter += 1
            except EntityFailed:
                pass
        if dist_counter > 0:
            self.inc('Good')
        else:
            self.inc('No valid Distribution')
            self.inc('Bad')
            raise EntityFailed('No valid Distribution')
