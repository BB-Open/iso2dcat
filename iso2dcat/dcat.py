# -*- coding: utf-8 -*-
from zope import component

from iso2dcat.component.interface import IRDFDatabase
from iso2dcat.entities.base import Base
from iso2dcat.entities.catalog import Catalog
from iso2dcat.entities.contactpoint import ContactPoint
from iso2dcat.entities.hierarchy import Hirarchy
from iso2dcat.entities.publisher import Publisher


class DCAT(Base):

    def __init__(self, node):
        self.node = node

    def run(self):
        self.logger.info('processing: {}'.format(self.node.fileIdentifier.getchildren()[0]))
        self.catalog = Catalog(self.node).run()
        self.publisher = Publisher(self.node).run()
        self.contact = ContactPoint(self.node).run()
        self.hirarchy = Hirarchy(self.node).run()

        self.logger.info('Writing Results')
        # todo: is this correct here or should be handled somewhere else
        # contact
        db = component.queryUtility(IRDFDatabase)
        data = self.contact.serialize(format='turtle')
        db.insert_data(data, 'text/turtle')
