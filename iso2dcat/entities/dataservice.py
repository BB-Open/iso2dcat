# -*- coding: utf-8 -*-
from iso2dcat.entities.resource import DcatResource


class DcatDataService(DcatResource):

    def run(self):
        SERVICE_DATASET_LINK_EXPR = './/srv:operatesOn'
        res = self.node.xpath(
            SERVICE_DATASET_LINK_EXPR,
            namespaces={
                'gmd': 'http://www.isotc211.org/2005/gmd',
                'srv': 'http://www.isotc211.org/2005/srv'
            }
        )
        if len(res) > 0:
            self.inc('service:has_parent')
        else:
            self.inc('service:no_parent')
