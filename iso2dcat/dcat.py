# -*- coding: utf-8 -*-
from zope import component

from iso2dcat.component.interface import IRDFDatabase
from iso2dcat.entities.base import Base
from iso2dcat.entities.catalog import Catalog
from iso2dcat.entities.contactpoint import ContactPoint
from iso2dcat.entities.hierarchy import Hirarchy
from iso2dcat.entities.publisher import Publisher


class CatalogBuilder(Base):

    def __init__(self):
        pass

    def run(self):
        self.catalog = Catalog(None).run()
        self.logger.info('Write Data to store')
        db = component.queryUtility(IRDFDatabase)
        data = self.catalog.serialize(format='turtle')
        db.insert_data(data, 'text/turtle')
        self.logger.info('Data written')


class DCAT(Base):

    def __init__(self, node):
        self.node = node

    def run(self):
        self.logger.info('processing: {}'.format(self.node.fileIdentifier.getchildren()[0]))
        self.hirarchy = Hirarchy(self.node).run()

        self.logger.info('Writing Results')
        db = component.queryUtility(IRDFDatabase)
        ttl = self.hirarchy.serialize(format='turtle')
        db.insert_data(ttl, 'text/turtle')
