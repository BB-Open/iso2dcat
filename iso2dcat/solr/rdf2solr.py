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
        VALUES ?s {{ <{}>  }}
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

SELECT DISTINCT ?c ?s ?p ?pt
    WHERE {{
        VALUES ?s {{ <{}>  }}
        ?c dcat:dataset ?s .
        ?c dct:publisher ?p .
        OPTIONAL {{
           ?p foaf:name ?pt
           }}
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
        if db_name is None:
            db_name = self.cfg.RDF2SOLR_SOURCE
        results = self.rdf4j.query_repository(db_name, ALL_DATASETS)
        triples = results['results']['bindings']
        res_dict = {}

        # For all datasets collect all attributes
        for res in triples:
            s_uri = res['s']['value']
            if s_uri not in res_dict:
                res_dict[s_uri] = {'id': s_uri}

            res_dict[s_uri]['dcterms_title'] = res['dt']['value']
            res_dict[s_uri]['dcterms_description'] = res['dd']['value']

        self.format_distribution(res_dict, db_name)
        self.format_publisher(res_dict, db_name)
        return res_dict

    def format_distribution(self, res_dict, db_name):
        if db_name is None:
            db_name = self.cfg.RDF2SOLR_SOURCE

        distribution_tags = ['dcterms_title', 'dcterms_license', 'dcat_accessURL', 'dcat_downloadURL', 'dcterms_format']

        # For all datasets collect all Distributions
        for dataset_uri in res_dict:
            sparql = DISTRIBUTIONS_FOR_DATASET.format(dataset_uri)
            results = self.rdf4j.query_repository(db_name, sparql)

            distributions = {}
            for res in results['results']['bindings']:
                distribution = res['d']['value']
                if distribution not in distributions:
                    distributions[distribution] = {}

                predicate = res['p']['value']
                if res['p']['type'] == 'uri':
                    tag = self.nsm.uri2prefix_name(predicate)
                else:
                    tag = predicate
                if tag in distribution_tags:
                    distributions[distribution][tag] = res['f']['value']

                if tag == 'dcterms_format':
                    format_string = res['f']['value']
                    if 'ft' in res:
                        format_string = res['ft']['value']

                    distributions[distribution]['dcterms_format'] = format_string

            distributions_json = json.dumps(distributions)
            res_dict[dataset_uri]['dcat_distribution'] = distributions_json

    def format_publisher(self, res_dict, db_name):
        publisher_tags = ['dcterms_title']

        for dataset_uri in res_dict:
            sparql = PUBLISHER_FOR_DATASET.format(dataset_uri)
            results = self.rdf4j.query_repository(db_name, sparql)
            res = results['results']['bindings'][0]
            if res['pt']:
                res_dict[dataset_uri]['dct_publisher'] = res['pt']['value']
            else:
                res_dict[dataset_uri]['dct_publisher'] = res['p']['value']



def main():
    rdf2solr = RDF2SOLR()
    rdf2solr.run()


if __name__ == '__main__':
    main()
