import io

from lxml import objectify
from rdflib import Graph, URIRef
from rdflib.namespace import FOAF, RDF

from iso2dcat.entities.base import Base, BaseDCM, BaseEntity
from iso2dcat.entities.languagemapper import LanguageMapper
from iso2dcat.namespace import NsManager, DCAT
from iso2dcat.statistics.stat import Stat
from tests.base import BaseTest, LoggerMockup, ConfigMockup, DCMMockup, RDFDatabaseMockup, abs_path


class TestBase(BaseTest):

    def test_logger(self):
        base = Base()
        self.assertIsInstance(base.logger, LoggerMockup)

    def test_config(self):
        base = Base()
        self.assertIsInstance(base.cfg, ConfigMockup)

    def test_stat(self):
        base = Base()
        self.assertIsInstance(base.stat, Stat)
        base.inc('test_base', no_uuid=True)
        self.assertTrue('Base' in base.stat.data)
        self.assertTrue('test_base' in base.stat.data['Base'])
        self.assertTrue(base.stat.data['Base']['test_base'] == 1)


class TestBaseDCM(BaseTest):

    def test_dcm(self):
        base_dcm = BaseDCM()
        self.assertIsInstance(base_dcm.dcm, DCMMockup)

    def test_language_mapper(self):
        base_dcm = BaseDCM()
        self.assertIsInstance(base_dcm.language_mapper, LanguageMapper)

    def test_rdf4j(self):
        base_dcm = BaseDCM()
        self.assertIsInstance(base_dcm.rdf4j, RDFDatabaseMockup)

    def test_nsm(self):
        base_dcm = BaseDCM()
        self.assertIsInstance(base_dcm.nsm, NsManager)

    def test_to_rdf4j(self):
        base_dcm = BaseDCM()
        rdf = Graph()
        rdf.add((URIRef('https://www.iso2dcat.de/'), RDF.type, FOAF.Agent))
        base_dcm.to_rdf4j(rdf)
        self.assertTrue(len(self.rdf4j.graph) == 1)


class TestBaseEntity(BaseTest):

    def setUp(self):
        super(TestBaseEntity, self).setUp()
        with open(abs_path('testdata/0a2c35a5-81b9-4ecd-a223-d40592c0ba12.xml'), 'rb') as rf:
            data = rf.read()
        xml_file = io.BytesIO(data)
        node = objectify.parse(xml_file).getroot()
        self.base_entity = BaseEntity(node)

    def test_namespaces(self):
        self.base_entity.set_namespaces()
        for prefix, URI in self.base_entity.nsm.nsm.namespaces():
            self.assertTrue((prefix, URIRef(URI)) in self.base_entity.rdf.namespace_manager.namespaces())

    def test_get_languages(self):
        langs = self.base_entity.get_languages()
        self.assertTrue(langs)
        self.assertTrue('de' in langs)
        self.assertTrue('Use cached Languages' not in self.logger.debug_messages)
        langs_again = self.base_entity.get_languages()
        self.assertTrue(langs == langs_again)
        self.assertTrue('Use cached Languages' in self.logger.debug_messages)

    def test_add_entity_type(self):
        self.base_entity.entity_type = None
        self.base_entity.add_entity_type()
        self.assertTrue(len(self.base_entity.rdf) == 0)
        self.base_entity.entity_type = DCAT.Dataset
        self.base_entity.add_entity_type()
        self.assertTrue(len(self.base_entity.rdf) == 1)
        self.assertTrue('Missing self.dcat_class' in self.logger.error_messages)


class TestBaseEntityNoLanguage(TestBaseEntity):

    def setUp(self):
        super(TestBaseEntity, self).setUp()
        with open(abs_path('testdata/bad.xml'), 'rb') as rf:
            data = rf.read()
        xml_file = io.BytesIO(data)
        node = objectify.parse(xml_file).getroot()
        self.base_entity = BaseEntity(node)

    def test_get_languages(self):
        langs = self.base_entity.get_languages()
        self.assertTrue(langs)
        self.assertTrue('' in langs)
        self.assertTrue('Use cached Languages' not in self.logger.debug_messages)
        langs_again = self.base_entity.get_languages()
        self.assertTrue(langs == langs_again)
        self.assertTrue('Use cached Languages' in self.logger.debug_messages)
