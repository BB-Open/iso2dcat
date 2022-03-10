# -*- coding: utf-8 -*-
from rdflib import DCTERMS, URIRef, Literal

from iso2dcat.entities.dataset import DcatDataset


class Tile(DcatDataset):

    def run(self):
        super(Tile, self).run()
        TILE_DATASET_LINK_EXPR = './/gmd:parentIdentifier'
        res = self.node.xpath(TILE_DATASET_LINK_EXPR, namespaces={'gmd': 'http://www.isotc211.org/2005/gmd'})

        dataset_ref = URIRef(self.base_uri + '#dcat_dataset_' + self.uuid)

        self.rdf.add((URIRef(self.uri), DCTERMS.isPartOf, dataset_ref))
        if len(res) > 0:
            self.inc('tile:has_parent')
        else:
            self.inc('tile:no_parent')

        return self.rdf
