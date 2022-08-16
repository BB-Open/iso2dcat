import simplejson as sj
from rdflib import Literal
from rdflib.namespace import DCTERMS

from iso2dcat.entities.base import BaseEntity
from iso2dcat.namespace import DCATDE

LICENSE = ".//gmd:resourceConstraints/gmd:MD_LegalConstraints/" \
          "gmd:otherConstraints/gco:CharacterString[text()]"


class License(BaseEntity):
    _stat_title = 'Licenses'
    _stat_desc = """Licenses are quite important for OpenData.
There are two possible ways to attach a License in DCAT-AP.de:
 * dcat:License
 * dcatapde:licenseAttributionByText
Dcat:Licenses are DCAT-URIs which have to conform to the GovData set of licenses.
Dcatapde:licenseAttributionByText can be any License text.
Dcat:License is strongly adviced so a not given dcat:license is counted as "Bad".

ISO can have more than one License.
All Licenses found by ISO2DCAT are scanned for GovData-Conform LicenseURI
which are then mapped to GovDATA License URIs.
Any other ISO license information is then stored as
dcatapde:licenseAttributionByText entities.
"""

    def __init__(self, node, rdf, parent_uri):
        super().__init__(node, rdf)
        self.parent_ressource_uri = parent_uri

    def run(self):
        self.inc('Processed')
        langs = self.get_languages()
        license_nodes = self.node.xpath(LICENSE, namespaces=self.nsm.namespaces)
        if not license_nodes:
            self.inc('No License')
            self.inc('Bad')
        licenses = {}

        URI_MAPPING = {
            'https://www.govdata.de/dl-de/by-2-0': 'http://dcat-ap.de/def/licenses/dl-by-de/2.0',
            'https://www.govdata.de/dl-de/zero-2-0': 'http://dcat-ap.de/def/licenses/dl-zero-de/2.0'
        }
        for license in license_nodes:
            if license.text[0] == '{' and license.text[-1] == '}':
                try:
                    license_obj = sj.loads(license.text)
                except Exception as e:
                    self.inc('JSON Error')
                    self.logger.error('JSON Error in: {}'.format(
                        self.node.fileIdentifier.getchildren()[0])
                    )
                    license_fixed = license.text.replace('\\\\', "\\")
                    license_obj = sj.loads(license_fixed)
                uri_in = license_obj['url']
                if uri_in in URI_MAPPING:
                    uri_out = URI_MAPPING[uri_in]
                else:
                    uri_out = uri_in
                licenses[DCTERMS.license] = self.make_uri_ref(uri_out)
                self.inc('dct:License')
                self.inc('Good')
            else:
                self.inc('dactapde:licenseAttributionByText')
                if len(langs) > 0:
                    for lang in langs:
                        licenses[DCATDE.licenseAttributionByText] = Literal(license.text, lang=lang)
                else:
                    licenses[DCATDE.licenseAttributionByText] = Literal(license.text)

        if len(list(licenses.keys())) > 0:
            for tag, license in licenses.items():
                self.add_tripel(self.make_uri_ref(self.parent_ressource_uri), tag, license)
