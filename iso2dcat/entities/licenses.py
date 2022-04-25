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
            'https://www.govdata.de/dl-de/by-2-0': 'http://dcat-ap.de/def/licenses/dl-by-de/2.0',
            'https://www.govdata.de/dl-de/zero-2-0' :'http://dcat-ap.de/def/licenses/dl-zero-de/2.0'
        }
        for license in license_nodes:
            try:
                license_obj = sj.loads(license.text)

                uri_in = license_obj['url']
                if uri_in in URI_MAPPING:
                    self.inc('Mapping')
                    uri_out = URI_MAPPING[uri_in]
                else:
                    self.inc('No Mapping')
                    uri_out = uri_in

                licenses[DCTERMS.license] = URIRef(uri_out)

                self.inc('DCAT License')
            except Exception as e:
                if license.text[0] == '{' and license.text[-1] == '}':
                    self.inc('JSON Error')
                    self.logger.error('JSON Error in: {}'.format(self.node.fileIdentifier.getchildren()[0]))
                for lang in langs:
                    licenses[DCATDE.licenseAttributionByText] = Literal(license, lang=lang)
                self.inc('DCAT licenseAttributionByText')

        if len(list(licenses.keys())) > 0:
            for tag, license in licenses.items():
                self.add_tripel(URIRef(self.parent_ressource_uri), tag, license)
