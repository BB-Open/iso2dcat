import json

import progressbar
import zope
from pkan_config.config import register_config, get_config

from iso2dcat.component.interface import IIsoCfg
from iso2dcat.entities.base import BaseDCM
from iso2dcat.format_mapper import register_formatmapper
from iso2dcat.license_mapper import register_licensemapper
from iso2dcat.log.log import register_logger
from iso2dcat.namespace import register_nsmanager
from iso2dcat.rdf_database.db import register_db
from iso2dcat.statistics.stat import register_stat

keys = []

ALL_DATASETS = """
prefix bds: <http://www.bigdata.com/rdf/search#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct: <http://purl.org/dc/terms/>
prefix foaf: <http://xmlns.com/foaf/0.1/>
prefix skos: <http://www.w3.org/2004/02/skos/core#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix inq: <http://inqbus.de/ns>


SELECT DISTINCT ?s ?dt ?dd ?type ?prio ?landing ?modified ?keyword
    WHERE {
        VALUES ?type { dcat:Dataset dcat:DataService }
        ?s a ?type .
        ?s dct:title ?dt .
        FILTER (lang(?dt) = "" || lang(?dt) = "de")
        OPTIONAL {
            ?s dct:description ?dd .
            FILTER (lang(?dd) = "" || lang(?dd) = "de")
        }
        OPTIONAL {
            ?s dcat:landingPage ?landing
        }
        OPTIONAL {
            ?s dct:modified ?modified
        }
        OPTIONAL {
            ?s dcat:keyword ?keyword
        }
        OPTIONAL {
            ?s inq:priority ?prio
        }
    }
"""

DCAT_THEMES = {
    "AGRI": "Landwirtschaft, Fischerei, Forstwirtschaft und Nahrungsmittel",
    "EDUC": 'Bildung, Kultur und Sport',
    "ENVI": 'Umwelt',
    "ENER": 'Energie',
    "TRAN": 'Verkehr',
    "TECH": 'Wissenschaft und Technologie',
    "ECON": 'Wirtschaft und Finanzen',
    "SOCI": 'Bevölkerung und Gesellschaft',
    "HEAL": 'Gesundheit',
    "GOVE": 'Regierung und öffentlicher Sektor',
    "REGI": 'Regionen und Städte',
    "JUST": 'Justiz, Rechtssystem und öffentliche Sicherheit',
    "INTR": 'Internationale Themen'
}

DISTRIBUTIONS_FOR_DATASET = """
prefix bds: <http://www.bigdata.com/rdf/search#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct: <http://purl.org/dc/terms/>
prefix foaf: <http://xmlns.com/foaf/0.1/>
prefix skos: <http://www.w3.org/2004/02/skos/core#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?s ?p ?d ?f ?ft
    WHERE {{
        VALUES ?p { dct:title dct:format dcat:accessURL dcat:downloadURL dct:description }
        ?s dcat:distribution ?d .
        ?d ?p ?f .
        OPTIONAL {{
           ?f dct:title ?ft
           }}
    }}
"""

PUBLISHER_FOR_DATASET = """
prefix bds: <http://www.bigdata.com/rdf/search#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct: <http://purl.org/dc/terms/>
prefix foaf: <http://xmlns.com/foaf/0.1/>
prefix skos: <http://www.w3.org/2004/02/skos/core#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?s ?p ?pt ?dp ?dpt
    WHERE {{
        ?c dcat:dataset ?s .
        ?c dct:publisher ?p .
        OPTIONAL {{
           ?p foaf:name ?pt
           }}
      OPTIONAL {{
  		?s dct:publisher ?dp
          OPTIONAL {{
          	?dp foaf:name ?dpt
          }}

  }}
        FILTER (lang(?pt) = "" || lang(?pt) = "de")
      FILTER (lang(?dpt) = "" || lang(?dpt) = "de")
    }}
"""

CONTACT_FOR_DATASET = """
prefix bds: <http://www.bigdata.com/rdf/search#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct: <http://purl.org/dc/terms/>
prefix foaf: <http://xmlns.com/foaf/0.1/>
prefix skos: <http://www.w3.org/2004/02/skos/core#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix vcard: <http://www.w3.org/2006/vcard/ns#>

SELECT DISTINCT ?s ?c ?p ?o
    WHERE {{
        ?s dcat:contactPoint ?c.
        ?c ?p ?o .
        FILTER (lang(?o) = "" || lang(?o) = "de")
    }}
    ORDER BY ASC(?c)
"""

THEMES_FOR_DATASET = """
prefix bds: <http://www.bigdata.com/rdf/search#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct: <http://purl.org/dc/terms/>
prefix foaf: <http://xmlns.com/foaf/0.1/>
prefix skos: <http://www.w3.org/2004/02/skos/core#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix vcard: <http://www.w3.org/2006/vcard/ns#>

SELECT DISTINCT ?s ?t
    WHERE {{
        ?s a dcat:Dataset .
        ?s dcat:theme ?t .
    }}
"""

LICENSE_FOR_DATASET = """
prefix bds: <http://www.bigdata.com/rdf/search#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct: <http://purl.org/dc/terms/>
prefix foaf: <http://xmlns.com/foaf/0.1/>
prefix skos: <http://www.w3.org/2004/02/skos/core#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix vcard: <http://www.w3.org/2006/vcard/ns#>
prefix dcatde: <http://dcat-ap.de/def/dcatde/>

SELECT DISTINCT ?s ?d ?dl ?dlt ?cl
    WHERE {{
        ?s a dcat:Dataset .
        OPTIONAL {
            ?s dcat:distribution ?d .
            OPTIONAL {
                ?d dct:license ?dl
            }
            OPTIONAL {
                ?d dcatde:licenseAttributionByText ?dlt
            }
        }
        OPTIONAL {
        ?c dcat:Catalog ?s .
        ?c dct:license ?cl
        }
    }}
"""

RIGHTSTATEMENT_FOR_DATASET = """
prefix bds: <http://www.bigdata.com/rdf/search#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct: <http://purl.org/dc/terms/>
prefix foaf: <http://xmlns.com/foaf/0.1/>
prefix skos: <http://www.w3.org/2004/02/skos/core#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix vcard: <http://www.w3.org/2006/vcard/ns#>
prefix dcatde: <http://dcat-ap.de/def/dcatde/>

SELECT DISTINCT ?s ?dl ?dlt
    WHERE {
        ?s a dcat:Dataset .

        ?s dcat:distribution ?d .
        ?d dct:accessRights ?dl
            OPTIONAL {
                ?dl rdfs:label ?dlt
            }

    }
"""

FORMAT_FOR_DATASET = """
prefix bds: <http://www.bigdata.com/rdf/search#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct: <http://purl.org/dc/terms/>
prefix foaf: <http://xmlns.com/foaf/0.1/>
prefix skos: <http://www.w3.org/2004/02/skos/core#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix vcard: <http://www.w3.org/2006/vcard/ns#>
prefix dcatde: <http://dcat-ap.de/def/dcatde/>

SELECT DISTINCT ?s ?df ?dft ?dfl
    WHERE {{
        ?s a dcat:Dataset .
        ?s dcat:distribution ?d .
        ?d dct:format ?df
        OPTIONAL {
        ?df dct:title ?dft
        }
        OPTIONAL {
        ?df skos:prefLabel ?dfl
        }
    }}
"""

DATASETS_FOR_DATASERVICES = """
prefix bds: <http://www.bigdata.com/rdf/search#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct: <http://purl.org/dc/terms/>
prefix foaf: <http://xmlns.com/foaf/0.1/>
prefix skos: <http://www.w3.org/2004/02/skos/core#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix vcard: <http://www.w3.org/2006/vcard/ns#>
prefix dcatde: <http://dcat-ap.de/def/dcatde/>

SELECT DISTINCT ?s ?d ?dt
    WHERE {{
        ?s a dcat:DataService .
        ?s dcat:servesDataset ?d .
        ?d dct:title ?dt .
    }}
"""

ENDPOINTS_FOR_DATASERVICES = """
prefix bds: <http://www.bigdata.com/rdf/search#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct: <http://purl.org/dc/terms/>
prefix foaf: <http://xmlns.com/foaf/0.1/>
prefix skos: <http://www.w3.org/2004/02/skos/core#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix vcard: <http://www.w3.org/2006/vcard/ns#>
prefix dcatde: <http://dcat-ap.de/def/dcatde/>

SELECT DISTINCT ?s ?de
    WHERE {{
        ?s a dcat:DataService .
        ?s dcat:endpointURL ?de .
    }}
"""


class UnknownTypeError(Exception):
    pass


class DataFormatter(BaseDCM):

    def __init__(self):
        super(DataFormatter, self).__init__()
        self.setup_components()

    def setup_components(self, args=None, env='Production', visitor=None, cfg=None):
        # Get the configuration
        if cfg:
            pass
        else:
            register_config(env=env)
            cfg = get_config()
        zope.component.provideUtility(cfg, IIsoCfg)

        # Setup the logging facility for this measurement ID
        register_logger(visitor=visitor)

        # Register the license mapper
        self.lcm = register_licensemapper()

        # Register the license mapper
        self.fm = register_formatmapper()

        self.logger.info('rdf2solr starting')
        # Register the namespace manager
        nsm = register_nsmanager()

        # Register statistics
        register_stat()
        self.stat.init(self)

        # Register RDF Database to write final results
        db = register_db()

    def format_distribution(self, res_dict, db_name):
        self.logger.info('Process Distributions')
        if db_name is None:
            db_name = self.cfg.RDF2SOLR_SOURCE

        sparql = DISTRIBUTIONS_FOR_DATASET
        results = self.rdf4j.query_repository(db_name, sparql)

        datasets = {}
        for res in progressbar.progressbar(results['results']['bindings']):
            dataset_uri = res['s']['value']
            if dataset_uri not in datasets:
                datasets[dataset_uri] = {}

            distribution = res['d']['value']
            if distribution not in datasets[dataset_uri]:
                datasets[dataset_uri][distribution] = {}

            predicate = self.nsm.uri2prefix_name(res['p']['value'])
            value = res['f']['value']
            datasets[dataset_uri][distribution][predicate] = value
            if 'ft' in res and predicate == 'dct_title':
                datasets[dataset_uri][distribution][predicate] = res['ft']['value']

        self.logger.info('Distributions processed')
        self.logger.info('Merge Distributions')

        for dataset_uri, distributions in progressbar.progressbar(datasets.items()):
            if dataset_uri not in res_dict:
                self.logger.info('Cannot add Distribution to dataset {}'.format(dataset_uri))
                continue
            # distributions_json = json.dumps(distributions)
            res_dict[dataset_uri]['dcat_distribution'] = distributions

        self.logger.info('Distributions merged')

    def format_publisher(self, res_dict, db_name):
        self.logger.info('Process Publishers')

        sparql = PUBLISHER_FOR_DATASET
        results = self.rdf4j.query_repository(db_name, sparql)

        for res in progressbar.progressbar(results['results']['bindings']):

            dataset_uri = res['s']['value']
            if dataset_uri not in res_dict:
                continue
            if res['dpt']:
                res_dict[dataset_uri]['dct_publisher'] = res['dpt']['value']
                res_dict[dataset_uri]['dct_publisher_facet'] = res['dpt']['value']
            elif res['pt']:
                res_dict[dataset_uri]['dct_publisher'] = res['pt']['value']
                res_dict[dataset_uri]['dct_publisher_facet'] = res['pt']['value']
            else:
                res_dict[dataset_uri]['dct_publisher'] = res['p']['value']
                res_dict[dataset_uri]['dct_publisher_facet'] = res['p']['value']

        self.logger.info('Publishers processed')

    def format_contact(self, res_dict, db_name, contact2json=True):
        self.logger.info('Process Contacts')

        sparql = CONTACT_FOR_DATASET
        results = self.rdf4j.query_repository(db_name, sparql)
        contacts = {}
        dataset_2_contacts = {}

        for res in progressbar.progressbar(results['results']['bindings']):
            dataset_uri = res['s']['value']
            contact_uri = res['c']['value']
            if contact_uri not in contacts:
                contacts[contact_uri] = {}
            tag = self.nsm.uri2prefix_name(res['p']['value'])
            contacts[contact_uri][tag] = res['o']['value']
            if dataset_uri not in dataset_2_contacts:
                dataset_2_contacts[dataset_uri] = [contact_uri, ]
            elif contact_uri not in dataset_2_contacts[dataset_uri]:
                dataset_2_contacts[dataset_uri].append(contact_uri)

        self.logger.info('Contacts processed')
        self.logger.info('Merge Contacts')

        for dataset_uri, contact_uris in progressbar.progressbar(dataset_2_contacts.items()):
            if dataset_uri not in res_dict:
                continue
            res_dict[dataset_uri]['dcat_contactPoint'] = []
            for contact_uri in contact_uris:
                if contact2json:
                    res_dict[dataset_uri]['dcat_contactPoint'].append(json.dumps(contacts[contact_uri]))
                else:
                    res_dict[dataset_uri]['dcat_contactPoint'].append(contacts[contact_uri])
        self.logger.info('Contacts merged')

    def format_themes(self, res_dict, db_name):
        self.logger.info('Process Themes')

        sparql = THEMES_FOR_DATASET
        results = self.rdf4j.query_repository(db_name, sparql)
        themes = {}

        for res in progressbar.progressbar(results['results']['bindings']):
            dataset_uri = res['s']['value']
            if dataset_uri not in themes:
                themes[dataset_uri] = []

            theme_abre = self.nsm.uri2prefix_name(res['t']['value']).split('_')[1]
            if theme_abre in DCAT_THEMES:
                themes[dataset_uri].append(DCAT_THEMES[theme_abre])

        self.logger.info('Themes processed')
        self.logger.info('Merge Themes')

        for dataset_uri, theme in progressbar.progressbar(themes.items()):
            if dataset_uri not in res_dict:
                continue
            res_dict[dataset_uri]['dcat_theme_facet'] = theme
        self.logger.info('Themes merged')

    def format_licenses(self, res_dict, db_name):
        self.logger.info('Process Licenses')

        sparql = LICENSE_FOR_DATASET
        results = self.rdf4j.query_repository(db_name, sparql)
        licenses = {}

        for res in progressbar.progressbar(results['results']['bindings']):
            dataset_uri = res['s']['value']
            if 'd' in res:
                dist_uri = res['d']['value']
            else:
                dist_uri = None
            if dataset_uri not in licenses:
                licenses[dataset_uri] = {}
            if 'dl' in res:
                license_uri = res['dl']['value']
                if license_uri not in self.lcm.mapping:
                    self.logger.info('Wrong License {}'.format(license_uri))
                    continue

                license_text = self.lcm.mapping[license_uri]
            elif 'dlt' in res:
                license_text = res['dlt']['value']
            else:
                license_text = None
                self.logger.info('No Licence for {}'.format(res['s']['value']))
            if license_text:
                licenses[dataset_uri][license_text] = 1
            if license_text and dist_uri:
                res_dict[dataset_uri]['dcat_distribution'][dist_uri]['dct_license'] = license_text

        self.logger.info('Licenses processed')
        self.logger.info('Merge Licenses')

        for dataset_uri, licence in progressbar.progressbar(licenses.items()):
            num_licenses = len(list(licence.keys()))
            if num_licenses == 1:
                res_dict[dataset_uri]['dct_license_facet'] = list(licence.keys())[0]
            elif num_licenses > 1:
                res_dict[dataset_uri]['dct_license_facet'] = list(licence.keys())[0]
            else:
                res_dict[dataset_uri]['dct_license_facet'] = "Keine Lizenz"

        self.logger.info('Licenses merged')

    def format_rightstatements(self, res_dict, db_name):
        self.logger.info('Process Right Statements')

        sparql = RIGHTSTATEMENT_FOR_DATASET
        results = self.rdf4j.query_repository(db_name, sparql)

        for res in progressbar.progressbar(results['results']['bindings']):
            dataset_uri = res['s']['value']
            if 'dlt' in res:
                statement_text = res['dlt']['value']
            elif 'dl' in res:
                statement_text = res['dl']['value']
            else:
                statement_text = None
                self.logger.info('No Rights Statement for {}'.format(res['s']['value']))

            if statement_text:
                res_dict[dataset_uri]['dct_rightsstatement'] = statement_text
        self.logger.info('Right Statements processed')

    def format_format(self, res_dict, db_name):
        self.logger.info('Process Fromats')

        sparql = FORMAT_FOR_DATASET
        results = self.rdf4j.query_repository(db_name, sparql)
        formats = {}

        for res in progressbar.progressbar(results['results']['bindings']):
            dataset_uri = res['s']['value']
            if dataset_uri not in formats:
                formats[dataset_uri] = []

            if 'dft' in res:
                format_text = res['dft']['value']
            elif 'dfl' in res:
                format_text = res['dfl']['value']
            else:
                format_uri = res['df']['value']
                if format_uri in self.fm.mapping:
                    format_text = self.fm.mapping[format_uri]
                else:
                    format_text = format_uri
                    self.logger.warning('No EU Format {}'.format(format_uri))

            self.logger.warning('Format is {}'.format(format_text))
            formats[dataset_uri].append(format_text)

        self.logger.info('Formats processed')
        self.logger.info('Merge Formats')

        for dataset_uri, format in progressbar.progressbar(formats.items()):
            if len(format) > 0:
                res_dict[dataset_uri]['dct_format_facet'] = format

        self.logger.info('Formats merged')

    def format_dataservice(self, res_dict, db_name, links2json=True):
        self.logger.info('Process Dataset links for DataServices')

        sparql = DATASETS_FOR_DATASERVICES
        results = self.rdf4j.query_repository(db_name, sparql)
        dataset_links = {}

        for res in progressbar.progressbar(results['results']['bindings']):
            dataservice_uri = res['s']['value']
            if dataservice_uri not in dataset_links:
                dataset_links[dataservice_uri] = []

            dataset_link = {
                'dct_title': res['dt']['value'],
                'dct_dataset': res['d']['value']
            }

            dataset_links[dataservice_uri].append(dataset_link)

        self.logger.info('Dataset Links for DataServicesDataset processed')
        self.logger.info('Merge Dataset Links')

        for dataservice_uri, links in progressbar.progressbar(dataset_links.items()):
            if len(links) > 0:
                if links2json:
                    res_dict[dataservice_uri]['dcat_servesDataset'] = json.dumps(links)
                else:
                    res_dict[dataservice_uri]['dcat_servesDataset'] = links

        self.logger.info('Dataset Links merged')

    def format_endpoints(self, res_dict, db_name, links2json=True):
        self.logger.info('Process endpointURLs for DataServices')

        sparql = ENDPOINTS_FOR_DATASERVICES
        results = self.rdf4j.query_repository(db_name, sparql)
        dataset_links = {}

        for res in progressbar.progressbar(results['results']['bindings']):
            dataservice_uri = res['s']['value']
            if dataservice_uri not in dataset_links:
                dataset_links[dataservice_uri] = []

            dataset_link = {
                'dcat_endpointURL': res['de']['value'],
            }

            dataset_links[dataservice_uri].append(dataset_link)

        self.logger.info('Dataset endpointURLs for DataServicesDataset processed')
        self.logger.info('Merge endpointURLs')

        for dataservice_uri, links in progressbar.progressbar(dataset_links.items()):
            if len(links) > 0:
                if links2json:
                    res_dict[dataservice_uri]['dcat_endpointURL'] = json.dumps(links)
                else:
                    res_dict[dataservice_uri]['dcat_endpointURL'] = []
                    for element in links:
                        res_dict[dataservice_uri]['dcat_endpointURL'].append(element['dcat_endpointURL'])

        self.logger.info('endpointURLs merged')

    def dist_2_json(self, res_dict):
        for d in res_dict:
            if 'dcat_distribution' in res_dict[d]:
                res_dict[d]['dcat_distribution'] = json.dumps(res_dict[d]['dcat_distribution'])

    def dist_to_text(self, dist):
        res = f"Die Distribution trägt den Titel '{dist['dct_title']}'"
        if 'dct_description' in dist:
            res += f"\nSie wird beschrieben als: {dist['dct_description']}"
        if 'dct_license' in dist:
            res += f"\nSie wurde lizensiert als '{dist['dct_license']}'."
        if 'dct_format' in dist:
            res += f"\nDie Distribution wurde als {dist['dct_format']} veröffentlicht."
        if 'dcat_downloadURL' in dist:
            res += f"\nDie Daten der Distribution stehen unter {dist['dcat_downloadURL']} als Download zur Verfügung."
        if 'dcat_accessURL' in dist:
            res += f"\nDie Distribution steht unter {dist['dcat_accessURL']} zur Verfügung."

        return res

    def contact_to_text(self, contact):
        res = "\nDer Kontakt beinhaltet folgende Angaben:"
        if 'vcard_fn' in contact:
            res += f"\n\tName: {contact['vcard_fn']}"
        if 'vcard_organization' in contact:
            res += f"\n\tOrganisation: {contact['vcard_organization']}"
        if 'dct_description' in contact:
            res += f"\n\tBeschreibung: {contact['dct_description']}"
        if 'vcard_hasEmail' in contact:
            res += f"\n\tEmail: {contact['vcard_hasEmail']}"
        if 'vcard_postal-code' in contact:
            res += f"\n\tPostleitzahl: {contact['vcard_postal-code']}"
        if 'vcard_locality' in contact:
            res += f"\n\tStadt: {contact['vcard_locality']}"
        if 'vcard_street-address' in contact:
            res += f"\n\tStraße: {contact['vcard_street-address']}"
        if 'vcard_region' in contact:
            res += f"\n\tRegion: {contact['vcard_region']}"
        if 'vcard_country-name' in contact:
            res += f"\n\tLand: {contact['vcard_country-name']}"
        if 'vcard_fax' in contact:
            res += f"\n\tFax: {contact['vcard_fax']}"
        if 'vcard_voice' in contact:
            res += f"\n\tTelefonnummer: {contact['vcard_voice']}"
        return res

    def common_fields_to_text(self, type, data):
        if 'dct_modified' in data:
            res = f"Der {type} '{data['dct_title']}' wurde zuletzt {data['dct_modified']} bearbeitet."
        else:
            res = f"Der {type} trägt den Titel '{data['dct_title']}'"
        if 'dct_description' in data:
            res += f"\nEr wird beschrieben als: {data['dct_description']}"
        if 'dcat_theme_facet' in data:
            res += f"\nEr beinhaltet Informationen zu den offiziellen Themenbereichen {', '.join(data['dcat_theme_facet'])}."
        if 'dcat_keyword' in data:
            res += f"\nEr beinhaltet Informationen zu den Themen {', '.join(data['dcat_keyword'])}."
        if 'dcat_landingpage' in data:
            res += f"\nDie Webseite verweist auf {data['dcat_landingpage']}."
        if 'dcat_contactPoint' in data:
            res += f"\nDer {type} '{data['dct_title']}' beinhaltet {len(data['dcat_contactPoint'])} Kontakte. Diese werden wie folgt beschrieben:"
            for contact in data['dcat_contactPoint']:
                res += '\n' + self.contact_to_text(contact)
        return res

    def dataset_to_text(self, dataset):
        res = self.common_fields_to_text('Datensatz', dataset)
        if 'dct_format_facet' in dataset:
            res += f"\nDer Datensatz wurde als {', '.join(set(dataset['dct_format_facet']))} veröffentlicht."
        if 'dcat_distribution' in dataset:
            res += f"\nDer Datensatz '{dataset['dct_title']}' beinhaltet {len(dataset['dcat_distribution'])} Veröffentlichungen. Diese werden wie folgt beschrieben:"
            for dist, dist_data in dataset['dcat_distribution'].items():
                res += '\n' + self.dist_to_text(dist_data)
        if 'dct_publisher' in dataset:
            res += f"\nDer Datensatz '{dataset['dct_title']}' wurde von '{dataset['dct_publisher']}' veröffentlicht."
        if 'dct_license_facet' in dataset:
            res += f"\nEr wurde lizensiert als '{dataset['dct_license_facet']}'."
        if 'dct_rightsstatement' in dataset:
            res += f"\nFür diesen Datensatz gelten folgende rechtliche Aussagen: {dataset['dct_rightsstatement']}"
        return res

    def dataservice_to_text(self, dataservice, all_data):
        res = self.common_fields_to_text('Dataservice', dataservice)

        if 'dcat_endpointURL' in dataservice:
            res += f"\nDer Datenservice '{dataservice['dct_title']}' beinhaltet {len(dataservice['dcat_endpointURL'])} Service URIs. "
            res += f"Diese verweisen auf {', '.join(dataservice['dcat_endpointURL'])}."

        if 'dcat_servesDataset' in dataservice:
            res += f"\nDer Datenservice '{dataservice['dct_title']}' beinhaltet {len(dataservice['dcat_servesDataset'])} Datensätze. Diese werden wie folgt beschrieben:"
            for dataset in dataservice['dcat_servesDataset']:
                res += '\n' + self.dataset_to_text(all_data[dataset['dct_dataset']])

        return res

    def dist_to_raw_text(self, dist):
        res = f"{dist['dct_title']}"
        if 'dct_description' in dist:
            res += f"\n{dist['dct_description']}"
        if 'dct_license' in dist:
            res += f"\n'{dist['dct_license']}'."
        if 'dct_format' in dist:
            res += f"\n{dist['dct_format']}."
        if 'dcat_downloadURL' in dist:
            res += f"\n{dist['dcat_downloadURL']}"
        if 'dcat_accessURL' in dist:
            res += f"\n{dist['dcat_accessURL']}"

        return res

    def contact_to_raw_text(self, contact):
        res = ''
        if 'vcard_fn' in contact:
            res += f"\n\t{contact['vcard_fn']}"
        if 'vcard_organization' in contact:
            res += f"\n\t{contact['vcard_organization']}"
        if 'dct_description' in contact:
            res += f"\n\t{contact['dct_description']}"
        if 'vcard_hasEmail' in contact:
            res += f"\n\t{contact['vcard_hasEmail']}"
        if 'vcard_postal-code' in contact:
            res += f"\n\t{contact['vcard_postal-code']}"
        if 'vcard_locality' in contact:
            res += f"\n\t{contact['vcard_locality']}"
        if 'vcard_street-address' in contact:
            res += f"\n\t{contact['vcard_street-address']}"
        if 'vcard_region' in contact:
            res += f"\n\t{contact['vcard_region']}"
        if 'vcard_country-name' in contact:
            res += f"\n\t{contact['vcard_country-name']}"
        if 'vcard_fax' in contact:
            res += f"\n\t{contact['vcard_fax']}"
        if 'vcard_voice' in contact:
            res += f"\n\t{contact['vcard_voice']}"
        return res

    def common_fields_to_raw_text(self, type, data):
        if 'dct_modified' in data:
            res = f"'{data['dct_title']}' {data['dct_modified']}"
        else:
            res = f"'{data['dct_title']}'"
        if 'dct_description' in data:
            res += f"\n{data['dct_description']}"
        if 'dcat_theme_facet' in data:
            res += f"\n{', '.join(data['dcat_theme_facet'])}."
        if 'dcat_keyword' in data:
            res += f"\n{', '.join(data['dcat_keyword'])}."
        if 'dcat_landingpage' in data:
            res += f"\n{data['dcat_landingpage']}."
        if 'dcat_contactPoint' in data:
            for contact in data['dcat_contactPoint']:
                res += '\n' + self.contact_to_raw_text(contact)
        return res

    def dataset_to_raw_text(self, dataset):
        res = self.common_fields_to_raw_text('Datensatz', dataset)
        if 'dct_format_facet' in dataset:
            res += f"\n{', '.join(set(dataset['dct_format_facet']))}"
        if 'dcat_distribution' in dataset:
            for dist, dist_data in dataset['dcat_distribution'].items():
                res += '\n' + self.dist_to_raw_text(dist_data)
        if 'dct_publisher' in dataset:
            res += f"\n{dataset['dct_publisher']}"
        # if 'dct_license_facet' in dataset:
        #     res += f"\n{dataset['dct_license_facet']}"
        if 'dct_rightsstatement' in dataset:
            res += f"\n{dataset['dct_rightsstatement']}"
        return res

    def dataservice_to_raw_text(self, dataservice, all_data):
        res = self.common_fields_to_raw_text('Dataservice', dataservice)

        if 'dcat_endpointURL' in dataservice:
            res += f"\n{', '.join(dataservice['dcat_endpointURL'])}"

        if 'dcat_servesDataset' in dataservice:
            for dataset in dataservice['dcat_servesDataset']:
                res += '\n' + self.dataset_to_raw_text(all_data[dataset['dct_dataset']])
        return res

    def format_data_as_dict(self, db_name=None, subs2json=True):
        self.logger.info('Process Datasets')

        if db_name is None:
            db_name = self.cfg.RDF2SOLR_SOURCE
        results = self.rdf4j.query_repository(db_name, ALL_DATASETS)
        triples = results['results']['bindings']
        res_dict = {}
        # For all datasets collect all attributes
        for res in progressbar.progressbar(triples):
            s_uri = res['s']['value']
            if s_uri not in res_dict:
                res_dict[s_uri] = {'id': s_uri}

            res_dict[s_uri]['dct_title'] = res['dt']['value']

            if 'landing' in res:
                res_dict[s_uri]['dcat_landingpage'] = res['landing']['value']
            if 'modified' in res:
                modified = res['modified']['value']
                res_dict[s_uri]['dct_modified'] = modified
            if 'keyword' in res and res['keyword']['value']:
                if 'dcat_keyword' in res_dict[s_uri]:
                    if res['keyword']['value'] not in res_dict[s_uri]['dcat_keyword']:
                        res_dict[s_uri]['dcat_keyword'].append(res['keyword']['value'])
                else:
                    res_dict[s_uri]['dcat_keyword'] = [res['keyword']['value']]

            if 'xml:lang' in res['dt']:
                res_dict[s_uri]['dct_title_lang'] = res['dt']['xml:lang']
            else:
                pass

            if 'dd' in res:
                res_dict[s_uri]['dct_description'] = res['dd']['value']
                if 'xml:lang' in res['dd']:
                    res_dict[s_uri]['dct_description_lang'] = res['dt']['xml:lang']
                else:
                    pass

            if 'type' in res:
                if res['type']['value'] == 'http://www.w3.org/ns/dcat#DataService':
                    res_dict[s_uri]['rdf_type'] = 'DataService'
                elif res['type']['value'] == 'http://www.w3.org/ns/dcat#Dataset':
                    res_dict[s_uri]['rdf_type'] = 'Dataset'
                else:
                    a = 10
            if 'prio' in res:
                res_dict[s_uri]['inq_priority'] = res['prio']['value']

        for res in res_dict.values():
            if 'inq_priority' not in res:
                res['inq_priority'] = 100

        self.logger.info('Datasets processed')
        self.format_distribution(res_dict, db_name)
        self.format_publisher(res_dict, db_name)
        self.format_contact(res_dict, db_name, contact2json=subs2json)
        self.format_themes(res_dict, db_name)
        self.format_licenses(res_dict, db_name)
        self.format_format(res_dict, db_name)
        self.format_dataservice(res_dict, db_name, links2json=subs2json)
        self.format_endpoints(res_dict, db_name, links2json=subs2json)
        self.format_rightstatements(res_dict, db_name)
        if subs2json:
            self.dist_2_json(res_dict)

        return res_dict

    def format_data_as_txt(self, db_name=None):
        data = self.format_data_as_dict(db_name, subs2json=False)
        result = {}
        for dataset in data:
            if data[dataset]['rdf_type'] == 'DataService':
                txt = self.dataservice_to_text(data[dataset], data)
                result[dataset] = txt
            elif data[dataset]['rdf_type'] == 'Dataset':
                txt = self.dataset_to_text(data[dataset])
                result[dataset] = txt
            else:
                raise UnknownTypeError(f'Unknown Type {data[dataset]["rdf_typef"]} for {dataset}')
        return result

    def format_data_as_raw_txt(self, db_name=None):
        data = self.format_data_as_dict(db_name, subs2json=False)
        result = {}
        for dataset in data:
            if data[dataset]['rdf_type'] == 'DataService':
                txt = self.dataservice_to_raw_text(data[dataset], data)
                result[dataset] = txt
            elif data[dataset]['rdf_type'] == 'Dataset':
                txt = self.dataset_to_raw_text(data[dataset])
                result[dataset] = txt
            else:
                raise UnknownTypeError(f'Unknown Type {data[dataset]["rdf_type"]} for {dataset}')
        return result

    def format_data_as_semantic_txt(self, db_name=None):
        data = self.format_data_as_dict(db_name, subs2json=False)
        result = {}
        for dataset in data:
            desc = ''
            if 'dct_description' in data[dataset]:
                desc += f"\n{data[dataset]['dct_description']}"
            txt = f"{data[dataset]['dct_title']} {desc}"
            result[dataset] = txt
        return result


if __name__ == '__main__':
    data_formatter = DataFormatter()
    res = data_formatter.format_data_as_semantic_txt()
    print(res)
