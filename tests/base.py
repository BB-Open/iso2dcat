import os
from pathlib import Path

import zope
from lxml import etree, objectify
from rdflib import Graph
from unittest2 import TestCase

from iso2dcat.component.interface import ILogger, IRDFDatabase, IDCM
from iso2dcat.dcm import DCM
from iso2dcat.main import Main


def abs_path(path):
    return Path(os.path.abspath(__file__)).parent / path


class ConfigMockup:
    FALLBACK_URL = 'https://www.iso2dcat.de'
    FALLBACK_CATALOG_NAME = 'Test'
    CSW_URI = None
    PARALLEL = False
    FROM_DISK = True
    CSW_PATH = abs_path('testdata')
    BATCH_COUNT = 1
    SAVE_DATASETS = False
    TOTAL_COUNT_LIMIT = 100
    DEFAULT_PRIORITY = 15
    # DCM will be mocked
    DCM_URI = 'test'


class LoggerMockup:

    def __init__(self):
        pass

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass

    def debug(self, msg):
        pass


class RDFDatabaseMockup:

    def __init__(self):
        self.graph = Graph()

    def insert_data(self, data, type):
        self.graph.parse(data=data, format=type)

    def reset(self):
        self.graph = Graph()


class DCMMockup(DCM):
    def __init__(self):
        super().__init__()
        self.cache_file = abs_path('testdata/dcm.json')


class BaseTest(TestCase):

    def setUp(self):
        self.setup_components()
        self.configer_etree()

    def tearDown(self):
        self.rdf4j.reset()

    def setup_components(self):
        self.cfg = ConfigMockup()
        self.logger = LoggerMockup()
        self.rdf4j = RDFDatabaseMockup()
        self.dcm = DCMMockup()
        zope.component.provideUtility(self.logger, ILogger)
        zope.component.provideUtility(self.rdf4j, IRDFDatabase)
        zope.component.provideUtility(self.dcm, IDCM)
        Main().setup_components(cfg=self.cfg)

    def configer_etree(self):
        self.parser = etree.XMLParser(remove_blank_text=True)
        self.lookup = etree.ElementNamespaceClassLookup(objectify.ObjectifyElementClassLookup())
        self.parser.setElementClassLookup(self.lookup)
