import io

from lxml import objectify
from rdflib import ConjunctiveGraph

from iso2dcat.entities.contactpoint import ContactPoint
from iso2dcat.exceptions import EntityFailed
from tests.base import BaseTest, abs_path


class TestContactPoint(BaseTest):
    def setUp(self):
        super(TestContactPoint, self).setUp()

    def contact_test(self, file):
        with open(abs_path(file), 'rb') as rf:
            data = rf.read()
        xml_file = io.BytesIO(data)
        node = objectify.parse(xml_file).getroot()
        self.contactpoint = ContactPoint(node, rdf=ConjunctiveGraph())
        self.contactpoint.set_namespaces()
        self.contactpoint.run()
        self.contactpoint.to_rdf4j(self.contactpoint.rdf)
        res = self.rdf4j.graph.query("""SELECT DISTINCT ?s WHERE {
                            ?s a vcard:Kind .
                            }
                        """)
        self.assertTrue(len(res) > 0)

    def test_pointOfContact(self):
        self.contact_test('testdata/0a2c35a5-81b9-4ecd-a223-d40592c0ba12.xml')

    def test_not_existing(self):
        with open(abs_path('testdata/bad.xml'), 'rb') as rf:
            data = rf.read()
        xml_file = io.BytesIO(data)
        node = objectify.parse(xml_file).getroot()
        self.contactpoint = ContactPoint(node, rdf=ConjunctiveGraph())
        self.assertRaises(EntityFailed, self.contactpoint.run)
