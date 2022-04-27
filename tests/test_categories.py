import io

from lxml import objectify
from rdflib import ConjunctiveGraph

from iso2dcat.entities.categories import CategoryKeywordMapper
from tests.base import BaseTest, abs_path


class TestKeyword(BaseTest):
    def setUp(self):
        super(TestKeyword, self).setUp()
        with open(abs_path('testdata/0a2c35a5-81b9-4ecd-a223-d40592c0ba12.xml'), 'rb') as rf:
            data = rf.read()
        xml_file = io.BytesIO(data)
        node = objectify.parse(xml_file).getroot()
        self.keywords = CategoryKeywordMapper(node, ConjunctiveGraph(), parent_uri='https://www.iso2dcat.de')

    def test_run(self):
        self.keywords.run()
        self.keywords.to_rdf4j(self.keywords.rdf)
        res = self.rdf4j.graph.query("""SELECT DISTINCT ?s WHERE {
                    ?s dcat:theme ?o .
                    }
                """)
        self.assertTrue(len(res) > 0)
        res = self.rdf4j.graph.query("""SELECT DISTINCT ?s WHERE {
                            ?s dcat:keyword ?o .
                            }
                        """)
        self.assertTrue(len(res) > 0)


class TestNoKeyword(BaseTest):
    def setUp(self):
        super(TestNoKeyword, self).setUp()
        with open(abs_path('testdata/bad.xml'), 'rb') as rf:
            data = rf.read()
        xml_file = io.BytesIO(data)
        node = objectify.parse(xml_file).getroot()
        self.keywords = CategoryKeywordMapper(node, ConjunctiveGraph(), parent_uri='https://www.iso2dcat.de')

    def test_run(self):
        self.keywords.run()
        self.keywords.to_rdf4j(self.keywords.rdf)
        res = self.rdf4j.graph.query("""SELECT DISTINCT ?s WHERE {
                    ?s dcat:theme ?o .
                    }
                """)
        self.assertTrue(len(res) == 0)
        res = self.rdf4j.graph.query("""SELECT DISTINCT ?s WHERE {
                            ?s dcat:keyword ?o .
                            }
                        """)
        self.assertTrue(len(res) == 0)


class TestGemet(BaseTest):
    def setUp(self):
        super(TestGemet, self).setUp()
        with open(abs_path('testdata/8ce339ec-c60b-4c26-a790-20f75756e255.xml'), 'rb') as rf:
            data = rf.read()
        xml_file = io.BytesIO(data)
        node = objectify.parse(xml_file).getroot()
        self.keywords = CategoryKeywordMapper(node, ConjunctiveGraph(), parent_uri='https://www.iso2dcat.de')

    def test_run(self):
        self.keywords.run()
        self.keywords.to_rdf4j(self.keywords.rdf)
        res = self.rdf4j.graph.query("""SELECT DISTINCT ?s WHERE {
                    ?s a skos:ConceptScheme .
                    }
                """)
        self.assertTrue(len(res) > 0)
        res = self.rdf4j.graph.query("""SELECT DISTINCT ?s WHERE {
                            ?s a skos:Concept .
                            }
                        """)
        self.assertTrue(len(res) > 0)


class TestOtherThesauri(BaseTest):
    def setUp(self):
        super(TestOtherThesauri, self).setUp()
        with open(abs_path('testdata/4263d50f-2ede-454c-a1c8-d5bf3f095418.xml'), 'rb') as rf:
            data = rf.read()
        xml_file = io.BytesIO(data)
        node = objectify.parse(xml_file).getroot()
        self.keywords = CategoryKeywordMapper(node, ConjunctiveGraph(), parent_uri='https://www.iso2dcat.de')

    def test_run(self):
        self.keywords.run()
        self.keywords.to_rdf4j(self.keywords.rdf)
        self.assertTrue('Missing Data for Thesauri BE/BB Schlagwortliste, Version 1.0' in self.logger.warn_messages)
