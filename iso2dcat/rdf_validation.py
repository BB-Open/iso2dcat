import time

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

ALL_DATASETS = """
prefix bds: <http://www.bigdata.com/rdf/search#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct: <http://purl.org/dc/terms/>
prefix foaf: <http://xmlns.com/foaf/0.1/>
prefix skos: <http://www.w3.org/2004/02/skos/core#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix inq: <http://inqbus.de/ns>


SELECT DISTINCT ?s ?dt ?dd ?type ?prio
    WHERE {
        VALUES ?type { dcat:Dataset dcat:DataService }
        ?s a ?type .
    }
"""

DISTRIBUTIONS_FOR_DATASET = """
prefix bds: <http://www.bigdata.com/rdf/search#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct: <http://purl.org/dc/terms/>
prefix foaf: <http://xmlns.com/foaf/0.1/>
prefix skos: <http://www.w3.org/2004/02/skos/core#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?s
    WHERE {{
        ?s a dcat:Distribution .
        <{dataset}> dcat:distribution ?s .
    }}
"""

PUBLISHER_FOR_DATASET = """
prefix bds: <http://www.bigdata.com/rdf/search#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct: <http://purl.org/dc/terms/>
prefix foaf: <http://xmlns.com/foaf/0.1/>
prefix skos: <http://www.w3.org/2004/02/skos/core#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?s
    WHERE {{
        ?s a foaf:Agent .
        <{dataset}> dct:publisher ?s .
    }}
"""


class RdfValidator(BaseDCM):

    def __init__(self):
        super(RdfValidator, self).__init__()
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

    def run(self, db_name=None, limit=None):
        self.logger.info('Loading rdf datasets')
        datasets = self.get_dataset_uris(db_name)
        if limit and limit < len(datasets):
            datasets = datasets[:limit]
        self.logger.info(len(datasets))
        start = time.time()
        for dataset in datasets:
            self.get_publisher(db_name, dataset)
            self.get_distributions(db_name, dataset)
        end = time.time()
        self.logger.info(f'Time needed {end-start}s')
        self.logger.info('rdf datasets loaded')

    def get_dataset_uris(self, db_name):
        self.logger.info('Process Datasets')

        if db_name is None:
            db_name = self.cfg.RDF2SOLR_SOURCE
        results = self.rdf4j.query_repository(db_name, ALL_DATASETS)
        triples = results['results']['bindings']
        dataset_uris = []
        for res in triples:
            s_uri = res['s']['value']
            if s_uri not in dataset_uris:
                dataset_uris.append(s_uri)
        return dataset_uris

    def get_distributions(self, db_name, dataset):
        if db_name is None:
            db_name = self.cfg.RDF2SOLR_SOURCE
        results = self.rdf4j.query_repository(db_name, DISTRIBUTIONS_FOR_DATASET.format(dataset=dataset))
        triples = results['results']['bindings']
        dist_uris = []
        # For all datasets collect all attributes
        for res in triples:
            s_uri = res['s']['value']
            if s_uri not in dist_uris:
                dist_uris.append(s_uri)
        return dist_uris

    def get_publisher(self, db_name, dataset):
        if db_name is None:
            db_name = self.cfg.RDF2SOLR_SOURCE
        results = self.rdf4j.query_repository(db_name, PUBLISHER_FOR_DATASET.format(dataset=dataset))
        triples = results['results']['bindings']
        publisher_uri = []
        # For all datasets collect all attributes
        for res in triples:
            s_uri = res['s']['value']
            if s_uri not in publisher_uri:
                publisher_uri.append(s_uri)
        return publisher_uri


def main():
    rdf_validator = RdfValidator()
    rdf_validator.run(limit=100)


if __name__ == '__main__':
    main()
