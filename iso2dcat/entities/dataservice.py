# -*- coding: utf-8 -*-
from rdflib import URIRef

from iso2dcat.entities.dataset import DcatDataset

from iso2dcat.entities.resource import DcatResource
from iso2dcat.namespace import DCAT


class DcatDataService(DcatResource):

    dcat_class = 'dcat_DataService'
    entity_type = DCAT.DataService

    def run(self):
        super(DcatDataService, self).run()
        SERVICE_DATASET_LINK_EXPR = './/srv:operatesOn'
        results = self.node.xpath(
            SERVICE_DATASET_LINK_EXPR,
            namespaces={
                'gmd': 'http://www.isotc211.org/2005/gmd',
                'srv': 'http://www.isotc211.org/2005/srv',
                'xlink': 'http://www.w3.org/1999/xlink',
            }
        )
        if len(results) > 0:
            self.inc('service:has_parent')
        else:
            self.inc('service:no_parent')

        for res in results:
            for item in res.items():
                if item[0] != '{http://www.w3.org/1999/xlink}href':
                    continue
                link =item[1]
                uuid = link.split('/')[-1]

                base_uri = self.dcm.file_id_to_baseurl(uuid, return_fallback=True)
                dataset_uri = base_uri + '#' + DcatDataset.dcat_class + '_' + uuid
                self.rdf.add([URIRef(self.uri), DCAT.servesDataset, URIRef(dataset_uri)])

#        dcat:endpointURL
