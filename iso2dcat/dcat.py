# -*- coding: utf-8 -*-
from rdflib import Graph

from iso2dcat.entities.base import BaseEntity, BaseDCM
from iso2dcat.entities.catalog import Catalog
from iso2dcat.entities.hierarchy import Hirarchy


class CatalogBuilder(BaseDCM):

    def run(self):
        catalog = Catalog(None, Graph())
        catalog.run()
        self.to_rdf4j(catalog.rdf)


class DCAT(BaseEntity):

    def run(self):
        self.logger.info('processing UUID: {}'.format(self.node.fileIdentifier.getchildren()[0]))
        hirarchy = Hirarchy(self.node, self.rdf)
        hirarchy.run()
