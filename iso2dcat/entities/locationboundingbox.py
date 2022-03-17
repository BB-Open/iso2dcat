from rdflib import URIRef
from rdflib.namespace import FOAF, RDF, DCTERMS, Namespace

from iso2dcat.entities.base import BaseEntity
from iso2dcat.exceptions import EntityFailed

LOCN = Namespace('https://www.w3.org/ns/locn')

LOCATION_QUERY = 'gmd:identificationInfo/*/gmd:extent/*/gmd:geographicElement|gmd:identificationInfo/*/srv:extent/*/gmd:geographicElement'

class LocationBoundingbox(BaseEntity):

    dcat_class = 'dct_Location'

    def __init__(self, node):

        super().__init__(node)
        self.directions = ['gmd:southBoundLatitude',
                          'gmd:northBoundLatitude',
                          'gmd:westBoundLongitude',
                          'gmd:eastBoundLongitude'
                          ]

    def run(self):
        self.rdf.add((URIRef(self.uri), RDF.type, DCTERMS.Location))
        subnode = self.node.xpath(LOCATION_QUERY, namespaces=self.nsm.namespaces)

        if not subnode:
            self.inc('bad')
            raise EntityFailed

        results = {}

        for element in subnode:

            for direction in self.directions:
                res = element.xpath('*/' + direction + '/gco:Decimal', namespaces=self.nsm.namespaces)
                if res:
                    results[direction] = res[0]
                else:
                    # incomplete location
                    results = {}
                    break
        if not results:
            self.inc('bad')
            raise EntityFailed
        else:
            self.inc('good')
        # todo: continue here
        return self.rdf
