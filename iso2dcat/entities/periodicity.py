from rdflib import URIRef
from rdflib.namespace import DCTERMS

from iso2dcat.entities.base import BaseEntity

QUERY = 'gmd:identificationInfo[1]/*/gmd:resourceMaintenance/*/gmd:maintenanceAndUpdateFrequency/*'


class AccrualPeriodicity(BaseEntity):

    def __init__(self, node, rdf, parent_uri):
        super().__init__(node, rdf)
        self.parent_ressource_uri = parent_uri
        self.mapping = {
            'continual': "http://publications.europa.eu/resource/authority/frequency/CONT",
            'fortnightly': "http://publications.europa.eu/resource/authority/frequency/BIWEEKLY",
            'biannually': "http://publications.europa.eu/resource/authority/frequency/ANNUAL_2",
            'annually': "http://publications.europa.eu/resource/authority/frequency/ANNUAL",
            'irregular': "http://publications.europa.eu/resource/authority/frequency/IRREG",
            'daily': "http://publications.europa.eu/resource/authority/frequency/DAILY",
            'weekly': "http://publications.europa.eu/resource/authority/frequency/WEEKLY",
            'monthly': "http://publications.europa.eu/resource/authority/frequency/MONTHLY",
            'quarterly': "http://publications.europa.eu/resource/authority/frequency/QUARTERLY",
            'unknown': "http://publications.europa.eu/resource/authority/frequency/UNKNOWN",
            'asNeeded': 'http://inspire.ec.europa.eu/metadata-codelist/MaintenanceFrequencyCode/asNeeded',
            'notPlanned': 'http://inspire.ec.europa.eu/metadata-codelist/MaintenanceFrequencyCode/notPlanned'
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
                self.add_tripel(
                    URIRef(self.parent_ressource_uri), DCTERMS.accrualPeriodicity, URIRef(self.mapping[value]))
            else:
                self.logger.warning('Missing AccrualPeriodicity Mapping for "' + value + '"')
