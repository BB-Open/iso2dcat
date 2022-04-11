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

# <gmd:hierarchyLevel>
#     <gmd:MD_ScopeCode codeList="https://standards.iso.org/iso/19139/resources/gmxCodelists.xml#MD_ScopeCode" codeListValue="service">service</gmd:MD_ScopeCode>
# </gmd:hierarchyLevel>

SCOPE_CODE_MAPPING = {
    'dataset': 'dcat:Dataset',
#    'series': 'dcat:Dataset',
#    'nonGeographicDataset': 'dcat:Dataset',
#    'service' : 'dcat:Distribution',
}


class Hirarchy(BaseEntity):

    dataset = 0
    distribution = 0
    service = 0

    stats = {}

    def run(self):
        HIRARCHY_EXPR = './/gmd:hierarchyLevel/gmd:MD_ScopeCode'

        res = self.node.xpath(HIRARCHY_EXPR, namespaces={'gmd': 'http://www.isotc211.org/2005/gmd'})

        if len(res) == 0:
            self.inc('bad')
            return None

        if len(res) > 1:
            self.logger.warning('gmd:hierarchyLevel: More than on hirarchy level given')
            self.inc('gray')

        hirarchy = res[0]

        if hirarchy not in SCOPE_CODE_MAPPING:
            self.inc('other')
            self.inc('good')
        else:
            self.inc('good')

        dcat_type = hirarchy

        self.inc(dcat_type)

        return self.process(hirarchy)

    def process(self, hirarchy):
# <gmd:transferOptions>
#     <gmd:MD_DigitalTransferOptions>
#             <gmd:onLine>
#                     <gmd:CI_OnlineResource>
#                             <gmd:linkage>
#                                     <gmd:URL>https://geobroker.geobasis-bb.de/gbss.php?MODE=GetProductInformation&amp;PRODUCTID=121181a5-3b7b-44db-9436-a0906f1f5d7c</gmd:URL>
#                             </gmd:linkage>

        if hirarchy == 'tile':
            return Tile(self.node, self.rdf).run()
        elif hirarchy == 'service':
            return DcatDataService(self.node, self.rdf).run()
        elif hirarchy == 'series':
            return DcatDataset(self.node, self.rdf).run()
        return DcatDataset(self.node, self.rdf).run()
