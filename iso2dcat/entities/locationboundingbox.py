from rdflib import Literal
from pkan_config.namespaces import RDF, DCTERMS

from iso2dcat.entities.base import BaseEntity
from iso2dcat.exceptions import EntityFailed
from pkan_config.namespaces import LOCN, GSP

LOCATION_QUERY = 'gmd:identificationInfo/*/gmd:extent/*/gmd:geographicElement/' \
                 'gmd:EX_GeographicBoundingBox|gmd:identificationInfo/*/srv:extent/' \
                 '*/gmd:geographicElement/gmd:EX_GeographicBoundingBox'

GEOMETRY = "<gml:Envelope srsName='http://www.opengis.net/def/crs/EPSG/0/4326'>" \
           "<gml:lowerCorner>{south} {west}</gml:lowerCorner>" \
           "<gml:upperCorner>{north} {east}</gml:upperCorner></gml:Envelope>"


class LocationBoundingbox(BaseEntity):
    dcat_class = 'dct_Location'

    _stat_title = 'dct:Location'
    _stat_desc = """Convert gmd:EX_GeographicBoundingBox to dct:Location by parsing directions:
    * gmd:southBoundLatitude
    * gmd:northBoundLatitude
    * gmd:westBoundLongitude
    * gmd:eastBoundLongitude
Good: Bounding box with directions found
Bad: Bounding Box missing or incomplete
"""

    def __init__(self, node, rdf):

        super().__init__(node, rdf)
        self.directions = ['gmd:southBoundLatitude',
                           'gmd:northBoundLatitude',
                           'gmd:westBoundLongitude',
                           'gmd:eastBoundLongitude'
                           ]

    def run(self):
        subnode = self.node.xpath(LOCATION_QUERY, namespaces=self.nsm.namespaces)
        self.inc('Processed')

        if not subnode:
            self.inc('Bad')
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
            self.inc('Bad')
            raise EntityFailed
        else:
            self.inc('Good')

        geometry_string = GEOMETRY.format(
            west=results['gmd:westBoundLongitude'],
            east=results['gmd:eastBoundLongitude'],
            north=results['gmd:northBoundLatitude'],
            south=results['gmd:southBoundLatitude'])

        uri_ref = self.make_uri_ref(self.uri)

        self.add_tripel(uri_ref, RDF.type, DCTERMS.Location)
        self.add_tripel(
            uri_ref,
            LOCN.geometry,
            Literal(geometry_string, datatype=GSP.gmlLiteral)
        )
