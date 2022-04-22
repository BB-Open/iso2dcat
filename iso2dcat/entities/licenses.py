import simplejson as sj
from rdflib import URIRef, Literal
from rdflib.namespace import DCTERMS

from iso2dcat.entities.base import BaseEntity
from iso2dcat.namespace import DCATDE

LICENSE = ".//gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco:CharacterString[text()]"


class License(BaseEntity):

    def __init__(self, node, rdf, parent_uri):
        super().__init__(node, rdf)
        self.parent_ressource_uri = parent_uri

    def run(self):
        langs = self.get_languages()
        license_nodes = self.node.xpath(LICENSE, namespaces=self.nsm.namespaces)
        if not license_nodes:
            self.inc('No License')
        licenses = {}

        URI_MAPPING = {
            'https://www.govdata.de/dl-de/by-2-0': 'http://dcat-ap.de/def/licenses/dl-by-de/2.0'
        }
        for license in license_nodes:
            try:
                license_obj = sj.loads(license.text)

                uri_in = license_obj['url']
                if uri_in in URI_MAPPING:
                    uri_out = URI_MAPPING[uri_in]
                else:
                    uri_out = uri_in

                licenses[DCTERMS.license] = URIRef(uri_out)

                self.inc('DCAT License')
            except Exception as e:
                for lang in langs:
                    licenses[DCATDE.licenseAttributionByText] = Literal(license, lang=lang)
                self.inc('DCAT licenseAttributionByText')

        if licenses is not None:
            for tag, license in licenses.items():
                self.rdf.add((URIRef(self.parent_ressource_uri), tag, license))