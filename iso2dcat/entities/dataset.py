# -*- coding: utf-8 -*-
from pkan_config.namespaces import DCAT

from iso2dcat.entities.distribution import Distribution
from iso2dcat.entities.resource import DcatResource
from iso2dcat.exceptions import EntityFailed

class DcatDataset(DcatResource):
    dcat_class = 'dcat_Dataset'
    entity_type = DCAT.Dataset

    _stat_title = 'dcat:Dataset'
    _stat_desc = 'A dcat:Dataset has to have a dct:title, ' \
                 'dct:description and at least one dcat:Distribution'

    def run(self):
        super(DcatDataset, self).run()

        self.inc('Processed')

        # catalog link
        # get base_uri without fallback to decide, if catalog suffix must be added
        base_uri = self.dcm.file_id_to_baseurl(self.uuid)

        catalog = base_uri + '#dcat_Catalog'

        uri_ref = self.make_uri_ref(self.uri)

        self.add_tripel(self.make_uri_ref(catalog), DCAT.dataset, uri_ref)

        try:
            distribution = Distribution(self.node, self.rdf, self.uri).run()
        except EntityFailed:
            self.inc('Bad')
            self.inc('No Distribution')
            raise EntityFailed('No Distribution')

        self.inc('Good')

        self.add_entity_type()
