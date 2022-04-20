from iso2dcat.csw import CSWProcessor
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
