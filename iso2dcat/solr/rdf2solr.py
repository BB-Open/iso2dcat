import progressbar
import pysolr

from iso2dcat.entities.base import BaseDCM

ALL_ENTITIES = """
prefix bds: <http://www.bigdata.com/rdf/search#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct: <http://purl.org/dc/terms/>
prefix foaf: <http://xmlns.com/foaf/0.1/>
prefix skos: <http://www.w3.org/2004/02/skos/core#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?s ?p ?o
    WHERE {
        VALUES ?type {  dcat:Dataset dcat:DataService dcat:Distribution dcat:Catalog foaf:Agent }
        ?s ?o ?p .
        ?s a ?type .
    }
"""


class RDF2SOLR(BaseDCM):

    def run(self, db_name=None):
        data_sets = self.format_data(db_name)
        self.solr = pysolr.Solr(self.cfg.SOLR_URI)
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
            tag = self.nsm.uri2prefix_name(res['o']['value'])
            predicate = res['p']['value']
            if res['p']['type'] == 'uri':
                value = self.nsm.uri2prefix_name(predicate)
            else:
                value = predicate
            if s_uri not in res_dict:
                res_dict[s_uri] = {'id': s_uri}

            res_dict[s_uri][tag] = value

        return res_dict

    def search(self, query_string, **kwargs):
        self.solr = pysolr.Solr(self.cfg.SOLR_URI, always_commit=True)
        return self.solr.search(query_string, **kwargs)

    def test1(self):

        add_params = {
            'facet.query' : 'dcterms_isPartOf=ns1_dcat_Dataset_121181a5-3b7b-44db-9436-a0906f1f5d7c'
        }
        res = self.search(
            '*Beer*',
            defType='edismax',
            qf='dcterms_title dcterms_description',
            facet='true',
            **add_params)
        return res
