# -*- coding: utf-8 -*-
from pkan_config.namespaces import DCAT

from iso2dcat.entities.dataset import DcatDataset
from iso2dcat.entities.licenses import License
from iso2dcat.entities.resource import DcatResource
from iso2dcat.exceptions import EntityFailed



class DcatDataService(DcatResource):

    _stat_title = 'dcat:DataServices'
    _stat_desc = 'A dcat:Dataservice has to have an endpointURI ' \
                 'and it should have dcat:Dataset which it serves'

    dcat_class = 'dcat_DataService'
    entity_type = DCAT.DataService

    def run(self):
        self.inc('Processed')
        super(DcatDataService, self).run()

        # catalog link
        # get base_uri without fallback to decide, if catalog suffix must be added
        base_uri = self.dcm.file_id_to_baseurl(self.uuid)

        catalog = base_uri + '#dcat_Catalog'

        uri_ref = self.make_uri_ref(self.uri)

        self.add_tripel(self.make_uri_ref(catalog), DCAT.service, uri_ref)

        SERVICE_DATASET_LINK_EXPR = './/srv:operatesOn'
        results = self.node.xpath(
            SERVICE_DATASET_LINK_EXPR,
            namespaces=self.nsm.namespaces
        )
        if len(results) > 0:
            self.inc('has dcat:Dataset')
        else:
            self.inc('no dcat:Dataset')

        uri_ref = self.make_uri_ref(self.uri)
        for res in results:
            for item in res.items():
                if item[0] != '{http://www.w3.org/1999/xlink}href':
                    continue
                link = item[1]
                uuid = link.split('/')[-1]

                base_uri = self.dcm.file_id_to_baseurl(uuid)
                dataset_uri = base_uri + '#' + DcatDataset.dcat_class + '_' + uuid
                self.add_tripel(uri_ref, DCAT.servesDataset, self.make_uri_ref(dataset_uri))
                self.add_tripel(self.make_uri_ref(catalog), DCAT.dataset, self.make_uri_ref(dataset_uri))

        #        dcat:endpointURL

        ENDPOINT_EXPR = ".//srv:connectPoint/gmd:CI_OnlineResource/gmd:linkage/*"
        results = self.node.xpath(
            ENDPOINT_EXPR,
            namespaces=self.nsm.namespaces
        )
        if len(results) == 0:
            self.inc('has no enpointURI')
            self.inc('Bad')
            raise EntityFailed('Missing Endpoint URI')
        else:
            self.inc('has enpointURI')

        for uri in results:
            self.add_tripel(uri_ref, DCAT.endpointURL, self.make_uri_ref(str(uri).strip()))

        licenses = License(self.node, self.rdf, self.uri)
        rdf = licenses.run()
        self.add_entity_type()

        self.inc('Good')
