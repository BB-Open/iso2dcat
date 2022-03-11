# -*- coding: utf-8 -*-
from iso2dcat.entities.resource import DcatResource
from iso2dcat.exceptions import EntityFailed
from iso2dcat.entities.base import DCAT


class DcatDataset(DcatResource):

    dcat_class = 'dcat_Dataset'
    entity_type = DCAT.Dataset

    def run(self):
        super(DcatDataset, self).run()
        return self.rdf
