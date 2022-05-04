import io

from lxml import objectify
from rdflib import ConjunctiveGraph

from iso2dcat.entities.foafdocuments import FoafDocuments
from tests.base import BaseTest, abs_path


class TestFoafDocument(BaseTest):

    def setUp(self):
        super(TestFoafDocument, self).setUp()

    def test_landing_page(self):
        path = abs_path('testdata/E04D90A6-35F5-480D-ABD7-640C48A6694D.xml')
        with open(path, 'rb') as rf:
            data = rf.read()
        xml_file = io.BytesIO(data)
        node = objectify.parse(xml_file).getroot()
        document = FoafDocuments(node,
                                 ConjunctiveGraph(),
                                 self.cfg.FALLBACK_URL
                                 )
        document.run()
        document.to_rdf4j(document.rdf)
        res = self.rdf4j.graph.query("""SELECT DISTINCT ?s WHERE {
                                                    ?s dcat:landingPage ?o .
                                                    }
                                                """)
        self.assertTrue(len(res) > 0)

    def test_foaf_page(self):
        path = abs_path('testdata/80543203-185e-4d17-8454-2a98bd405182.xml')
        with open(path, 'rb') as rf:
            data = rf.read()
        xml_file = io.BytesIO(data)
        node = objectify.parse(xml_file).getroot()
        document = FoafDocuments(node,
                                 ConjunctiveGraph(),
                                 self.cfg.FALLBACK_URL
                                 )
        document.run()
        document.to_rdf4j(document.rdf)
        res = self.rdf4j.graph.query("""
        prefix foaf: <http://xmlns.com/foaf/0.1/>

        SELECT DISTINCT ?s WHERE {
            ?s foaf:page ?o .
            }
        """)
        self.assertTrue(len(res) > 0)

    def test_bad(self):
        with open(abs_path('testdata/bad.xml'), 'rb') as rf:
            data = rf.read()
        xml_file = io.BytesIO(data)
        node = objectify.parse(xml_file).getroot()
        document = FoafDocuments(node,
                                 ConjunctiveGraph(),
                                 self.cfg.FALLBACK_URL
                                 )
        document.run()
        document.to_rdf4j(document.rdf)
        res = self.rdf4j.graph.query("""
                prefix foaf: <http://xmlns.com/foaf/0.1/>

                SELECT DISTINCT ?s WHERE {
                    ?s foaf:page ?o .
                    }
                """)
        self.assertTrue(len(res) == 0)
        res = self.rdf4j.graph.query("""SELECT DISTINCT ?s WHERE {
                                            ?s dcat:landingPage ?o .
                                        }
                                    """)
        self.assertTrue(len(res) == 0)
