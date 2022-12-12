from datetime import datetime

from rdflib import Literal
from pkan_config.namespaces import DCTERMS, XSD

from iso2dcat.entities.base import BaseEntity

DATE_QUERY = "gmd:identificationInfo[1]/*/gmd:citation/*" \
             "/gmd:date/*[gmd:dateType/*/@codeListValue=$role]/gmd:date/*"


class DateMapper(BaseEntity):
    cached_keywords = {}

    _stat_title = "dct:modified and dct:issued"
    _stat_desc = "Both are used to mark updated Dcat Information and set to datetime.now()"

    def __init__(self, node, rdf, parent_uri):
        super().__init__(node, rdf)
        self.parent_ressource_uri = parent_uri
        self.roles = ['revision', 'creation', 'publication']

    def run(self):
        # todo: Role fields as fields on data
        self.inc('Processed')
        self.inc('Good')
        parent_uri_ref = self.make_uri_ref(self.parent_ressource_uri)
        self.add_tripel(
            parent_uri_ref,
            DCTERMS.modified,
            Literal(datetime.now(), datatype=XSD.dateTimeStamp)
        )
        self.add_tripel(
            parent_uri_ref,
            DCTERMS.issued,
            Literal(datetime.now(), datatype=XSD.dateTimeStamp)
        )
