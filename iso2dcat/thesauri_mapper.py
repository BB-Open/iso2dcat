from pyrdf4j.errors import QueryFailed
from zope import component

from iso2dcat.component.interface import ILicenseMapper, IGemetMapper
from iso2dcat.entities.base import BaseEntity
from iso2dcat.path_utils import abs_file_path

KNOWN_THESAURI = {
    'GEMET - INSPIRE themes, version 1.0': IGemetMapper
}

GEMET_QUERY = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX dct: <http://purl.org/dc/terms/>

        SELECT ?s WHERE {{ ?s dct:title ?label FILTER (lcase(str(?label)) = '{keyword}').}}"""


class GemetMapper(BaseEntity):
    cached_keywords = {}

    def __init__(self, node, rdf=None, parent=None):
        super().__init__(node, rdf, parent)
        self.base = 'http://www.eionet.europa.eu/gemet/'
        try:
            self.rdf.parse('https://inspire.ec.europa.eu/theme/theme.de.rdf')
        except Exception as e:
            print(e)
            self.rdf.parse(abs_file_path('iso2dcat/data/theme.de.rdf'))

    def keyword_to_uri(self, keyword):
        # todo: why is there a problem with utf-8 character?
        if keyword in self.cached_keywords:
            return self.cached_keywords[keyword]
        keyword_clean = str(keyword).lower()
        res = self.rdf.query(GEMET_QUERY.format(keyword=keyword_clean))
        uris = []
        for row in res:
            uris.append(row[0])
        self.cached_keywords[keyword] = uris
        return uris

# MAPPING = """
# prefix skos: <http://www.w3.org/2004/02/skos/core#>
#
# SELECT  ?s ?pl
#     WHERE {{
#     	?s a skos:Concept .
#       	?s skos:prefLabel ?pl .
#     }}
# """
#
#
# class LicenseMapper(BaseEntity):
#
#     def __init__(self, node, rdf=None, parent=None):
#         super(LicenseMapper, self).__init__(node, rdf, parent)
#
#         try:
#             self.rdf.parse('https://www.dcat-ap.de/def/licenses/20210721.rdf')
#         except Exception as e:
#             self.rdf.parse(abs_file_path('iso2dcat/data/20210721.rdf'))
#
#         self.mapping = {}
#
#         result = self.rdf.query(MAPPING)
#
#         for res in result:
#             self.mapping[str(res[0])] = str(res[1])


def register_thesauri():
    gemet_mapper = GemetMapper(None)
    component.provideUtility(gemet_mapper, IGemetMapper)
    return gemet_mapper

