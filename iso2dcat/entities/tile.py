# -*- coding: utf-8 -*-
from pkan_config.namespaces import DCTERMS

from iso2dcat.entities.dataset import DcatDataset


class Tile(DcatDataset):

    _stat_title = "Tiles"
    _stat_desc = """
A dcat:Dataset has to have a dct:title, dct:description and at least one dcat:Distribution.
Tiles are special Dataset with dct:isPartOf
"""

    def run(self):
        super(Tile, self).run()
        TILE_DATASET_LINK_EXPR = './/gmd:parentIdentifier'
        results = self.node.xpath(
            TILE_DATASET_LINK_EXPR,
            namespaces=self.nsm.namespaces
        )

        for res in results:
            parent_uuid = res.getchildren()[0]
            base_uri = self.dcm.file_id_to_baseurl(parent_uuid)
            dataset_uri = base_uri + '#' + DcatDataset.dcat_class + '_' + parent_uuid

            self.add_tripel(self.make_uri_ref(self.uri), DCTERMS.isPartOf, self.make_uri_ref(dataset_uri))

        if len(res) > 0:
            self.inc('tile:has_parent')
        else:
            self.inc('tile:no_parent')
