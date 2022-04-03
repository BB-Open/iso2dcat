import json

import progressbar
import pysolr
import zope
from pkan_config.config import register_config, get_config

from iso2dcat.component.interface import IIsoCfg
from iso2dcat.entities.base import BaseDCM
from iso2dcat.log.log import register_logger
from iso2dcat.namespace import register_nsmanager
from iso2dcat.rdf_database.db import register_db
from iso2dcat.statistics.stat import register_stat

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

ALL_DATASETS = """
prefix bds: <http://www.bigdata.com/rdf/search#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct: <http://purl.org/dc/terms/>
prefix foaf: <http://xmlns.com/foaf/0.1/>
prefix skos: <http://www.w3.org/2004/02/skos/core#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?s ?dt ?dd
    WHERE {
        VALUES ?type {dcat:Dataset}
        ?s a ?type .
        ?s dct:description ?dd .
  		?s dct:title ?dt .
  		FILTER (lang(?dd) = "" || lang(?dd) = "de")
  		FILTER (lang(?dt) = "" || lang(?dt) = "de")
    }
"""

DISTRIBUTIONS_FOR_DATASET = """
prefix bds: <http://www.bigdata.com/rdf/search#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct: <http://purl.org/dc/terms/>
prefix foaf: <http://xmlns.com/foaf/0.1/>
prefix skos: <http://www.w3.org/2004/02/skos/core#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?s ?p ?d ?f ?ft
    WHERE {{
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

SELECT DISTINCT ?s ?p ?pt
    WHERE {{
        ?c dcat:dataset ?s .
        ?c dct:publisher ?p .
        OPTIONAL {{
           ?p foaf:name ?pt
           }}
        FILTER (lang(?pt) = "" || lang(?pt) = "de")
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


class RDF2SOLR(BaseDCM):

    def __init__(self):
        super(RDF2SOLR, self).__init__()
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

        self.logger.info('rdf2solr starting')
        # Register the namespace manager
        nsm = register_nsmanager()

        # Register statistics
        register_stat()

        # Register RDF Database to write final results
        db = register_db()

    def run(self, db_name=None):
        self.logger.info('Loading rdf datasets')
        data_sets = self.format_data(db_name)
        self.logger.info('rdf datasets loaded')
        self.solr = pysolr.Solr(self.cfg.SOLR_URI, auth=('writer','Sas242!!'))
        self.logger.info('writing datasets to solr')
        for key, data_set in progressbar.progressbar(data_sets.items()):
            self.solr.add(data_set)
        self.solr.commit()
        self.logger.info('datasets written to solr')
        self.logger.info('rdf2solr finished')

    def format_data(self, db_name):
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

            res_dict[s_uri]['dcterms_title'] = res['dt']['value']
            res_dict[s_uri]['dcterms_description'] = res['dd']['value']

        self.logger.info('Datasets processed')

        self.format_distribution(res_dict, db_name)
        self.format_publisher(res_dict, db_name)
        self.format_contact(res_dict, db_name)
        self.format_themes(res_dict, db_name)
        return res_dict

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
            if 'ft' in res and predicate == 'dcterms_title':
                datasets[dataset_uri][distribution][predicate] = res['ft']['value']

        self.logger.info('Distributions processed')
        self.logger.info('Merge Distributions')

        for dataset_uri, distributions in progressbar.progressbar(datasets.items()):
            if dataset_uri not in res_dict:
                self.logger.info('Cannot add Distribution to dataset {}'.format(dataset_uri))
                continue
            distributions_json = json.dumps(distributions)
            res_dict[dataset_uri]['dcat_distribution'] = distributions_json

        self.logger.info('Distributions merged')

    def format_publisher(self, res_dict, db_name):
        self.logger.info('Process Publishers')

        sparql = PUBLISHER_FOR_DATASET
        results = self.rdf4j.query_repository(db_name, sparql)

        for res in progressbar.progressbar(results['results']['bindings']):

            dataset_uri = res['s']['value']
            if dataset_uri not in res_dict:
                continue
            if res['pt']:
                res_dict[dataset_uri]['dcterms_publisher'] = res['pt']['value']
                res_dict[dataset_uri]['dcterms_publisher_facet'] = res['pt']['value']
            else:
                res_dict[dataset_uri]['dcterms_publisher'] = res['p']['value']
                res_dict[dataset_uri]['dcterms_publisher_facet'] = res['p']['value']

        self.logger.info('Publishers processed')

    def format_contact(self, res_dict, db_name):
        self.logger.info('Process Contacts')

        sparql = CONTACT_FOR_DATASET
        results = self.rdf4j.query_repository(db_name, sparql)
        contacts = {}

        for res in progressbar.progressbar(results['results']['bindings']):
            dataset_uri = res['s']['value']
            if dataset_uri not in contacts:
                contacts[dataset_uri] = {}
            tag = self.nsm.uri2prefix_name(res['p']['value'])
            contacts[dataset_uri][tag] = res['o']['value']

        self.logger.info('Contacts processed')
        self.logger.info('Merge Contacts')

        for dataset_uri, contact in progressbar.progressbar(contacts.items()):
            if dataset_uri not in res_dict:
                continue
            res_dict[dataset_uri]['dcat_contactPoint'] = json.dumps(contact)
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
                themes[dataset_uri].append( DCAT_THEMES[theme_abre])

        self.logger.info('Themes processed')
        self.logger.info('Merge Themes')

        for dataset_uri, theme in progressbar.progressbar(themes.items()):
            if dataset_uri not in res_dict:
                continue
            res_dict[dataset_uri]['dcat_theme_facet'] = theme
        self.logger.info('Themes merged')



def main():
    rdf2solr = RDF2SOLR()
    rdf2solr.run()


if __name__ == '__main__':
    main()
