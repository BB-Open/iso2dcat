import io

from lxml import objectify

from iso2dcat.entities.dataservice import DcatDataset
from iso2dcat.exceptions import EntityFailed
from tests.base import BaseTest, abs_path


class TestDataset(BaseTest):

    def setUp(self):
        super(TestDataset, self).setUp()
        with open(abs_path('testdata/80543203-185e-4d17-8454-2a98bd405182.xml'), 'rb') as rf:
            data = rf.read()
        xml_file = io.BytesIO(data)
        node = objectify.parse(xml_file).getroot()
        self.service = DcatDataset(node)

    def test_run(self):
        self.service.run()
        self.service.to_rdf4j(self.service.rdf)
        res = self.rdf4j.graph.query("""SELECT DISTINCT ?s WHERE {
                                            ?s a dcat:Dataset .
                                            }
                                        """)
        self.assertTrue(len(res) == 1)


class TestBadDataSet(BaseTest):
    def setUp(self):
        super(TestBadDataSet, self).setUp()
        with open(abs_path('testdata/bad.xml'), 'rb') as rf:
            data = rf.read()
        xml_file = io.BytesIO(data)
        node = objectify.parse(xml_file).getroot()
        self.service = DcatDataset(node)

    def test_run(self):
        self.assertRaises(EntityFailed, self.service.run)
