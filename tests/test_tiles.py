import io

from lxml import objectify

from iso2dcat.entities.tile import Tile
from tests.base import BaseTest, abs_path


class TestTiles(BaseTest):

    def setUp(self):
        super(TestTiles, self).setUp()
        path = abs_path('testdata/80543203-185e-4d17-8454-2a98bd405182.xml')
        with open(path, 'rb') as rf:
            data = rf.read()
        xml_file = io.BytesIO(data)
        node = objectify.parse(xml_file).getroot()
        self.tile = Tile(node)

    def test_run(self):
        self.tile.run()
        self.tile.to_rdf4j(self.tile.rdf)
        res = self.rdf4j.graph.query("""SELECT DISTINCT ?s WHERE {
                                            ?s a dcat:Dataset .
                                            }
                                        """)
        self.assertTrue(len(res) == 1)

        res = self.rdf4j.graph.query("""
        PREFIX dct: <http://purl.org/dc/terms/>

        SELECT DISTINCT ?s WHERE {{
            <{uri}> dct:isPartOf ?s .
            }}
        """.format(uri=self.tile.uri))
        self.assertTrue(len(res) == 1)
