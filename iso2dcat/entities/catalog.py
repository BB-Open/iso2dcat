# -*- coding: utf-8 -*-
from iso2dcat.component.interface import IStat, ICatalog
from iso2dcat.entities.base import BaseEntity
import zope


@zope.interface.implementer(ICatalog)
class Catalog(BaseEntity):

    catalog = {}

    def run(self):
        identifier = self.node.fileIdentifier.getchildren()[0].text
        if identifier in self.dcm.dcm:
            key = self.dcm.dcm[identifier]['publisher']
            self.inc('good')
        else:
            self.inc('bad')
