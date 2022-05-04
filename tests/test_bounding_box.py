import io

from lxml import objectify
from rdflib import ConjunctiveGraph

from iso2dcat.entities.foafdocuments import FoafDocuments
from iso2dcat.entities.locationboundingbox import LocationBoundingbox
from iso2dcat.exceptions import EntityFailed
from tests.base import BaseTest, abs_path


class TestLocation(BaseTest):

    def setUp(self):
        super(TestLocation, self).setUp()

    def test_location(self):
        path = abs_path('testdata/80543203-185e-4d17-8454-2a98bd405182.xml')
        with open(path, 'rb') as rf:
            data = rf.read()
        xml_file = io.BytesIO(data)
        node = objectify.parse(xml_file).getroot()
        location = LocationBoundingbox(node, ConjunctiveGraph())
        location.run()
        location.to_rdf4j(location.rdf)
        res = self.rdf4j.graph.query("""
        PREFIX dct: <http://purl.org/dc/terms/>
        SELECT DISTINCT ?s WHERE {
                                                    ?s a dct:Location .
                                                    }
                                                """)
        self.assertTrue(len(res) > 0)

    def test_bad(self):
        with open(abs_path('testdata/bad.xml'), 'rb') as rf:
            data = rf.read()
        xml_file = io.BytesIO(data)
        node = objectify.parse(xml_file).getroot()
        location = LocationBoundingbox(node, ConjunctiveGraph())
        self.assertRaises(EntityFailed, location.run)
        location.to_rdf4j(location.rdf)
        res = self.rdf4j.graph.query("""
        PREFIX dct: <http://purl.org/dc/terms/>
        SELECT DISTINCT ?s WHERE {
                                                            ?s a dct:Location .
                                                            }
                                                        """)
        self.assertTrue(len(res) == 0)
