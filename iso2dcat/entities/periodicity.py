from pkan_config.namespaces import DCTERMS, SKOS

from iso2dcat.entities.base import BaseEntity

QUERY = 'gmd:identificationInfo[1]/*/gmd:resourceMaintenance/*/gmd:maintenanceAndUpdateFrequency/*'
BASE_URL = 'http://publications.europa.eu/resource/authority/frequency'


class AccrualPeriodicity(BaseEntity):

    _stat_title = "dct:accrualPeriodicity"
    _stat_desc = """Convert gmd:maintenanceAndUpdateFrequency to dct:accrualPeriodicity
Each Detail line shows one value found in ISO-Files.

MAPPING:
continual: http://publications.europa.eu/resource/authority/frequency/CONT
fortnightly: http://publications.europa.eu/resource/authority/frequency/BIWEEKLY
biannually: http://publications.europa.eu/resource/authority/frequency/ANNUAL_2
annually: http://publications.europa.eu/resource/authority/frequency/ANNUAL
irregular: http://publications.europa.eu/resource/authority/frequency/IRREG
daily: http://publications.europa.eu/resource/authority/frequency/DAILY
weekly: http://publications.europa.eu/resource/authority/frequency/WEEKLY
monthly: http://publications.europa.eu/resource/authority/frequency/MONTHLY
quarterly: http://publications.europa.eu/resource/authority/frequency/QUARTERLY
unknown: http://publications.europa.eu/resource/authority/frequency/UNKNOWN
asNeeded: http://publications.europa.eu/resource/authority/frequency/IRREG
notPlanned: http://publications.europa.eu/resource/authority/frequency/UNKNOWN
"""

    def __init__(self, node, rdf, parent_uri):
        super().__init__(node, rdf)
        self.parent_ressource_uri = parent_uri
        self.mapping = {
            'continual': "CONT",
            'fortnightly': "BIWEEKLY",
            'biannually': "ANNUAL_2",
            'annually': "ANNUAL",
            'irregular': "IRREG",
            'daily': "DAILY",
            'weekly': "WEEKLY",
            'monthly': "MONTHLY",
            'quarterly': "QUARTERLY",
            'unknown': "UNKNOWN",
            'asNeeded':
                "IRREG",
            'notPlanned':
                "UNKNOWN",
        }

    def run(self):
        values = self.node.xpath(QUERY, namespaces=self.nsm.namespaces)
        if not values:
            self.inc('Bad')
            self.logger.warning('No AccrualPeriodicity found')
        else:
            self.logger.debug('Found AccrualPeriodicity {values}'.format(values=values))
            self.inc('Good')
        for value in values:
            if value in self.mapping:
                self.inc(value)
                field = self.mapping[value]
                field = BASE_URL + '/' + field
                self.add_tripel(self.make_uri_ref(field), SKOS.inScheme, self.make_uri_ref(BASE_URL))
                self.add_tripel(
                    self.make_uri_ref(self.parent_ressource_uri),
                    DCTERMS.accrualPeriodicity,
                    self.make_uri_ref(field)
                )
            else:
                self.logger.warning('Missing AccrualPeriodicity Mapping for "' + value + '"')
