from iso2dcat.entities.dataservice import DcatDataService
from iso2dcat.entities.dataset import DcatDataset
from iso2dcat.main import Main
from tests.base import BaseTest


class TestMain(BaseTest):

    def test_main(self):
        main = Main()
        main.run(cfg=self.cfg)
        res = self.rdf4j.graph.query("""SELECT DISTINCT ?s WHERE {
                                    ?s a dcat:Dataset .
                                    }
                                """)
        self.assertTrue(len(res) > 0)
        res = self.rdf4j.graph.query("""SELECT DISTINCT ?s WHERE {
                                            ?s a dcat:DataService .
                                            }
                                        """)
        self.assertTrue(len(res) > 0)

        # bad data is not generated as entity
        uri_bad = self.cfg.FALLBACK_URL + '#' + DcatDataset.dcat_class + '_bad'
        res = self.rdf4j.graph.query("""SELECT DISTINCT ?o WHERE {{
                    <{uri}> ?p ?o
                }}""".format(uri=uri_bad))
        print(res)
        self.assertTrue(len(res) == 0)
        uri_bad = self.cfg.FALLBACK_URL + '#' + DcatDataService.dcat_class + '_bad'
        res = self.rdf4j.graph.query("""SELECT DISTINCT ?o WHERE {{
                    <{uri}> ?p ?o
                }}""".format(uri=uri_bad))
        self.assertTrue(len(res) == 0)

        # catalogs generated
        res = self.rdf4j.graph.query("""SELECT DISTINCT ?s WHERE {
                    ?s a foaf:Agent .
                    }
                """)
        self.assertTrue(len(res) > 0)
        res = self.rdf4j.graph.query("""SELECT DISTINCT ?s WHERE {
                            ?s a dcat:Catalog .
                            }
                        """)
        self.assertTrue(len(res) > 0)
