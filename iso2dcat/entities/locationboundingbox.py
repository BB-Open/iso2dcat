from rdflib import URIRef, Literal
from rdflib.namespace import FOAF, RDF, DCTERMS, Namespace

from iso2dcat.entities.base import BaseEntity
from iso2dcat.exceptions import EntityFailed
from iso2dcat.namespace import LOCN, GSP

LOCATION_QUERY = 'gmd:identificationInfo/*/gmd:extent/*/gmd:geographicElement/gmd:EX_GeographicBoundingBox|gmd:identificationInfo/*/srv:extent/*/gmd:geographicElement/gmd:EX_GeographicBoundingBox'

GEOMETRY = "<gml:Envelope srsName='http://www.opengis.net/def/crs/EPSG/0/4326'><gml:lowerCorner>{south} {west}</gml:lowerCorner><gml:upperCorner>{north} {east}</gml:upperCorner></gml:Envelope>"

class LocationBoundingbox(BaseEntity):

    dcat_class = 'dct_Location'

    def __init__(self, node, rdf):

        super().__init__(node, rdf)
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
                res = element.xpath(direction + '/gco:Decimal', namespaces=self.nsm.namespaces)
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

        geometry_string = GEOMETRY.format(
            west=results['gmd:westBoundLongitude'],
            east=results['gmd:eastBoundLongitude'],
            north=results['gmd:northBoundLatitude'],
            south=results['gmd:southBoundLatitude'])

        self.rdf.add((URIRef(self.uri), RDF.type, DCTERMS.Location))
        self.rdf.add((URIRef(self.uri), LOCN.geometry, Literal(geometry_string, datatype=GSP.gmlLiteral)))

