from iso2dcat.entities.base import BaseEntity


# <gmd:hierarchyLevel>
#     <gmd:MD_ScopeCode codeList="https://standards.iso.org/iso/19139/resources/gmxCodelists.xml#MD_ScopeCode" codeListValue="service">service</gmd:MD_ScopeCode>
# </gmd:hierarchyLevel>

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
            self.inc('bad')
        else:
            self.inc('good')

        dcat_type = hirarchy

        self.inc(dcat_type)

        self.process(hirarchy)

    def process(self, hirarchy):
# <gmd:transferOptions>
#     <gmd:MD_DigitalTransferOptions>
#             <gmd:onLine>
#                     <gmd:CI_OnlineResource>
#                             <gmd:linkage>
#                                     <gmd:URL>https://geobroker.geobasis-bb.de/gbss.php?MODE=GetProductInformation&amp;PRODUCTID=121181a5-3b7b-44db-9436-a0906f1f5d7c</gmd:URL>
#                             </gmd:linkage>
        TILE_DATASET_LINK_EXPR = './/gmd:parentIdentifier'

        if hirarchy == 'tile':
            res = self.node.xpath(TILE_DATASET_LINK_EXPR, namespaces={'gmd': 'http://www.isotc211.org/2005/gmd'})
            if len(res) > 0:
                self.inc('tile:has_parent')
            else:
                self.inc('tile:no_parent')
        elif hirarchy == 'service':
            SERVICE_DATASET_LINK_EXPR = './/srv:operatesOn'
            res = self.node.xpath(
                SERVICE_DATASET_LINK_EXPR,
                namespaces={
                    'gmd': 'http://www.isotc211.org/2005/gmd',
                    'srv' : 'http://www.isotc211.org/2005/srv'
                }
            )
            if len(res) > 0:
                self.inc('service:has_parent')
            else:
                self.inc('service:no_parent')
        elif hirarchy == 'series':
            a = 10

