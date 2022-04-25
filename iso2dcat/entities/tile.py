# -*- coding: utf-8 -*-
from rdflib import URIRef
from rdflib.namespace import DCTERMS

from iso2dcat.entities.dataset import DcatDataset


class Tile(DcatDataset):

    def run(self):
        super(Tile, self).run()
        TILE_DATASET_LINK_EXPR = './/gmd:parentIdentifier'
        results = self.node.xpath(TILE_DATASET_LINK_EXPR, namespaces={'gmd': 'http://www.isotc211.org/2005/gmd'})

        for res in results:
            parent_uuid = res.getchildren()[0]
            base_uri = self.dcm.file_id_to_baseurl(parent_uuid, return_fallback=True)
            dataset_uri = base_uri + '#' + DcatDataset.dcat_class + '_' + parent_uuid

            self.add_tripel(URIRef(self.uri), DCTERMS.isPartOf, URIRef(dataset_uri))

        if len(res) > 0:
            self.inc('tile:has_parent')
        else:
            self.inc('tile:no_parent')
