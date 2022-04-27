from rdflib import Graph

from iso2dcat.dcat import CatalogBuilder
from iso2dcat.entities.catalog import Catalog
from tests.base import BaseTest


class TestCatalog(BaseTest):

    def setUp(self):
        super(TestCatalog, self).setUp()
        self.dcm.run()
        self.catalog = CatalogBuilder()

    def test_run(self):
        self.catalog.run()
        res = self.rdf4j.graph.query("""SELECT DISTINCT ?s WHERE {
            ?s a foaf:Agent .
            }
        """)
        self.assertTrue(len(res) == 9)
        res = self.rdf4j.graph.query("""SELECT DISTINCT ?s WHERE {
                    ?s a dcat:Catalog .
                    }
                """)
        self.assertTrue(len(res) == 9)
