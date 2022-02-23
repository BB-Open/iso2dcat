# -*- coding: utf-8 -*-
from iso2dcat.entities.base import Base
from iso2dcat.entities.catalog import Catalog
from iso2dcat.entities.contactpoint import ContactPoint
from iso2dcat.entities.publisher import Publisher


class DCAT(Base):

    def __init__(self, node):
        self.node = node

    def run(self):
        self.catalog = Catalog(self.node).run()
        self.publisher = Publisher(self.node).run()
        self.contact = ContactPoint(self.node).run()
