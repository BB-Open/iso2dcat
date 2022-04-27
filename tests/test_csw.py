from iso2dcat.csw import CSWProcessor
from iso2dcat.entities.dataservice import DcatDataService
from iso2dcat.entities.dataset import DcatDataset
from tests.base import BaseTest


class TestCSWProcessor(BaseTest):

    def setUp(self):
        super(TestCSWProcessor, self).setUp()
        self.dcm.run()
        self.processor = CSWProcessor()

    def test_init(self):
        self.assertTrue(self.processor)
        self.assertTrue(self.processor.csw is None)
        self.assertTrue('No Uri provided, make sure you use File Mode' in self.logger.error_messages)

    def test_run(self):
        self.processor.run()
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
