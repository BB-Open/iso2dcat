from iso2dcat.entities.base import BaseEntity
from iso2dcat.entities.dataservice import DcatDataService
from iso2dcat.entities.dataset import DcatDataset
# Possible values
# <CodeDefinition gml:id="MD_ScopeCode_attribute">
# <CodeDefinition gml:id="MD_ScopeCode_attributeType">
# <CodeDefinition gml:id="MD_ScopeCode_collectionHardware">
# <CodeDefinition gml:id="MD_ScopeCode_collectionSession">
# <CodeDefinition gml:id="MD_ScopeCode_dataset">
# <CodeDefinition gml:id="MD_ScopeCode_series">
# <CodeDefinition gml:id="MD_ScopeCode_nonGeographicDataset">
# <CodeDefinition gml:id="MD_ScopeCode_dimensionGroup">
# <CodeDefinition gml:id="MD_ScopeCode_feature">
# <CodeDefinition gml:id="MD_ScopeCode_featureType">
# <CodeDefinition gml:id="MD_ScopeCode_propertyType">
# <CodeDefinition gml:id="MD_ScopeCode_fieldSession">
# <CodeDefinition gml:id="MD_ScopeCode_software">
# <CodeDefinition gml:id="MD_ScopeCode_service">
# <CodeDefinition gml:id="MD_ScopeCode_model">
# <CodeDefinition gml:id="MD_ScopeCode_tile">
from iso2dcat.entities.tile import Tile
from iso2dcat.exceptions import EntityFailed

SCOPE_CODE_MAPPING = {
    'dataset': 'dcat:Dataset',
    #    'series': 'dcat:Dataset',
    #    'nonGeographicDataset': 'dcat:Dataset',
    #    'service' : 'dcat:Distribution',
}


class Hierarchy(BaseEntity):
    _stat_title = 'Statistics in ISO datatset types'
    _stat_desc = 'ISO has several dataset types. ' \
                 'ISO2DCAT represents ISO:service as dcat:DataService and all other as dcat:DataSet'

#    dataset = 0
#    distribution = 0
#    service = 0

    def run(self):
        HIERARCHY_EXPR = './/gmd:hierarchyLevel/gmd:MD_ScopeCode'

        res = self.node.xpath(
            HIERARCHY_EXPR,
            namespaces=self.nsm.namespaces
        )

        if len(res) == 0:
            self.inc('Bad')
            return None

        if len(res) > 1:
            self.logger.warning('gmd:hierarchyLevel: More than on hirarchy level given')
            self.inc('gray')

        hierarchy = res[0]

        if hierarchy not in SCOPE_CODE_MAPPING:
            self.inc('other')

        dcat_type = hierarchy

        self.inc(dcat_type)

        return self.process(hierarchy)

    def process(self, hierarchy):
        # <gmd:transferOptions>
        #     <gmd:MD_DigitalTransferOptions>
        #             <gmd:onLine>
        #                     <gmd:CI_OnlineResource>
        #                             <gmd:linkage>
        #                                     <gmd:URL>https://geobroker.geobasis-bb.de/gbss.php?MODE=GetProductInformation&amp;PRODUCTID=121181a5-3b7b-44db-9436-a0906f1f5d7c</gmd:URL>
        #                             </gmd:linkage>
        self.inc('Processed')
        try:
            if hierarchy == 'tile':
                result = Tile(self.node, self.rdf).run()
            elif hierarchy == 'service':
                result = DcatDataService(self.node, self.rdf).run()
            elif hierarchy == 'series':
                result = DcatDataset(self.node, self.rdf).run()
            else:
                result = DcatDataset(self.node, self.rdf).run()
        except EntityFailed as e:
            self.inc('Bad')
            raise e

        self.inc('Good')
        return result
