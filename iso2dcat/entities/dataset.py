# -*- coding: utf-8 -*-

from iso2dcat.entities.distribution import Distribution
from iso2dcat.entities.resource import DcatResource
from iso2dcat.exceptions import EntityFailed
from iso2dcat.namespace import DCAT


class DcatDataset(DcatResource):
    dcat_class = 'dcat_Dataset'
    entity_type = DCAT.Dataset

    _stat_title = 'dcat:Dataset'
    _stat_desc = 'A dcat:Dataset has to have a dct:title, ' \
                 'dct:description and at least one dcat:Distribution'

    def run(self):
        super(DcatDataset, self).run()

        self.inc('Processed')

        try:
            distribution = Distribution(self.node, self.rdf, self.uri).run()
        except EntityFailed:
            self.inc('Bad')
            self.inc('No Distribution')
            raise EntityFailed('No Distribution')

        self.inc('Good')

        self.add_entity_type()
