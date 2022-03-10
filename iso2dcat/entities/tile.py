# -*- coding: utf-8 -*-
from iso2dcat.entities.dataset import DcatDataset


class Tile(DcatDataset):

    def run(self):

        TILE_DATASET_LINK_EXPR = './/gmd:parentIdentifier'
        res = self.node.xpath(TILE_DATASET_LINK_EXPR, namespaces={'gmd': 'http://www.isotc211.org/2005/gmd'})
        if len(res) > 0:
            self.inc('tile:has_parent')
        else:
            self.inc('tile:no_parent')
