from datetime import datetime

from rdflib import Literal, URIRef
from rdflib.namespace import DCTERMS, XSD

from iso2dcat.entities.base import BaseEntity

DATE_QUERY = "gmd:identificationInfo[1]/*/gmd:citation/*/gmd:date/*[gmd:dateType/*/@codeListValue=$role]/gmd:date/*"


class DateMapper(BaseEntity):
    cached_keywords = {}

    def __init__(self, node, rdf, parent_uri):
        super().__init__(node, rdf)
        self.parent_ressource_uri = parent_uri
        self.roles = ['revision', 'creation', 'publication']

    def run(self):
        # todo: Role fields as fields on data
        self.rdf.add(
            (URIRef(self.parent_ressource_uri), DCTERMS.modified, Literal(datetime.now(), datatype=XSD.dateTimeStamp)))
        self.rdf.add(
            (URIRef(self.parent_ressource_uri), DCTERMS.issued, Literal(datetime.now(), datatype=XSD.dateTimeStamp)))
