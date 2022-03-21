import progressbar
import pysolr
import zope

from iso2dcat.component.interface import ICfg
from iso2dcat.config import register_config
from iso2dcat.dcm import register_dcm
from iso2dcat.entities.base import BaseDCM
from iso2dcat.entities.languagemapper import register_languagemapper
from iso2dcat.log.log import register_logger
from iso2dcat.namespace import register_nsmanager
from iso2dcat.rdf_database.db import register_db
from iso2dcat.statistics.stat import register_stat

ALL_ENTITIES = """
prefix bds: <http://www.bigdata.com/rdf/search#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct: <http://purl.org/dc/terms/>
prefix foaf: <http://xmlns.com/foaf/0.1/>
prefix skos: <http://www.w3.org/2004/02/skos/core#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?s ?p ?o
    WHERE {
        VALUES ?type {dcat:Dataset dcat:DataService dcat:Distribution dcat:Catalog foaf:Agent}
        ?s ?p ?o .
        ?s a ?type .
    }
"""


class RDF2SOLR(BaseDCM):

    def __init__(self):
        super(RDF2SOLR, self).__init__()
        self.setup_components()

    def setup_components(self, args=None, env='Production', visitor=None, cfg=None):
        # Get the configuration
        if cfg:
            zope.component.provideUtility(cfg, ICfg)
        else:
            register_config(args, env=env)

        # Setup the logging facility for this measurement ID
        register_logger(visitor=visitor)

        # Register the namespace manager
        nsm = register_nsmanager()

        # Register statistics
        register_stat()

        # Register RDF Database to write final results
        db = register_db()

#        # Register the DCM-Interface
#        dcm = register_dcm()

#        # register language mapper
#        language_mapper = register_languagemapper()

    def run(self, db_name=None):
        data_sets = self.format_data(db_name)
        self.solr = pysolr.Solr(self.cfg.SOLR_URI, auth=('writer','Sas242!!'))
#        self.solr.delete(q='*:*', commit=True)
#        self.solr.commit()
        data_len = len(data_sets)
        for key, data_set in progressbar.progressbar(data_sets.items()):
            self.solr.add(data_set)
        self.solr.commit()

    def format_data(self, db_name):
        if db_name is None:
            db_name = self.cfg.WRITE_TO
        results = self.rdf4j.query_repository(db_name, ALL_ENTITIES)
        triples = results['results']['bindings']
        res_dict = {}
        for res in triples:
            s_uri = res['s']['value']
            if s_uri not in res_dict:
                res_dict[s_uri] = {'id': s_uri}

            predicate = res['p']['value']
            if res['p']['type'] == 'uri':
                tag = self.nsm.uri2prefix_name(predicate)
            else:
                tag = predicate

            object = res['o']['value']
            value = object

            res_dict[s_uri][tag] = value

        return res_dict

    def search(self, query_string, **kwargs):
        self.solr = pysolr.Solr(self.cfg.SOLR_URI, always_commit=True, auth=('reader','Sas242!!'),)
        return self.solr.search(query_string, **kwargs)

    def test1(self):
#        'facet.query': 'dcterms_isPartOf=ns1_dcat_Dataset_121181a5-3b7b-44db-9436-a0906f1f5d7c'

        add_params = {
            'suggest.dictionary' : 'mySuggester',
            'suggest.q' :'Beer',
        }
        res = self.search(
            '*Beer*',
#            defType='edismax',
#            qf='dcterms_title dcterms_description',
#            facet='true',
            **add_params)
        return res


def main():
    rdf2solr = RDF2SOLR()
    rdf2solr.run()

if __name__ == '__main__':
    main()
