import io

from lxml import objectify

from iso2dcat.entities.dataservice import DcatDataService
from iso2dcat.exceptions import EntityFailed
from tests.base import BaseTest, abs_path


class TestDataservice(BaseTest):

    def setUp(self):
        super(TestDataservice, self).setUp()
        path = abs_path('testdata/0b240f09-a9e5-4bc1-9351-c2a9a9b2cfab.xml')
        with open(path, 'rb') as rf:
            data = rf.read()
        xml_file = io.BytesIO(data)
        node = objectify.parse(xml_file).getroot()
        self.service = DcatDataService(node)

    def test_run(self):
        self.service.run()
        self.service.to_rdf4j(self.service.rdf)
        res = self.rdf4j.graph.query("""SELECT DISTINCT ?s WHERE {
                                            ?s a dcat:DataService .
                                            }
                                        """)
        self.assertTrue(len(res) == 1)
        res = self.rdf4j.graph.query("""SELECT DISTINCT ?s WHERE {
                                            ?s a dcat:DataService .
                                            ?s dcat:endpointURL ?o .
                                            }
                                        """)
        self.assertTrue(len(res) == 1)


class TestDataServiceNoParent(TestDataservice):

    def setUp(self):
        super(TestDataServiceNoParent, self).setUp()
        path = abs_path('testdata/724acaf6-670f-4f1d-ac1c-fbadd3f9e93e.xml')
        with open(path, 'rb') as rf:
            data = rf.read()
        xml_file = io.BytesIO(data)
        node = objectify.parse(xml_file).getroot()
        self.service = DcatDataService(node)


class TestBadDataService(BaseTest):
    def setUp(self):
        super(TestBadDataService, self).setUp()
        with open(abs_path('testdata/bad.xml'), 'rb') as rf:
            data = rf.read()
        xml_file = io.BytesIO(data)
        node = objectify.parse(xml_file).getroot()
        self.service = DcatDataService(node)

    def test_run(self):
        self.assertRaises(EntityFailed, self.service.run)
