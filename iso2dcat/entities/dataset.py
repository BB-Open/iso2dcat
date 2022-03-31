# -*- coding: utf-8 -*-
from rdflib import URIRef

from iso2dcat.entities.resource import DcatResource
from iso2dcat.exceptions import EntityFailed
from iso2dcat.entities.base import DCAT
from iso2dcat.entities.distribution import Distribution

class DcatDataset(DcatResource):

    dcat_class = 'dcat_Dataset'
    entity_type = DCAT.Dataset

    def run(self):
        super(DcatDataset, self).run()

        distribution = Distribution(self.node, self.uri).run()

        return self.rdf
