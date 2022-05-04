from zope import component

from iso2dcat.component.interface import ILicenseMapper
from iso2dcat.entities.base import BaseEntity
from iso2dcat.path_utils import abs_file_path

MAPPING = """
prefix skos: <http://www.w3.org/2004/02/skos/core#>

SELECT  ?s ?pl
    WHERE {{
        ?s a skos:Concept .
        ?s skos:prefLabel ?pl .
    }}
"""


class LicenseMapper(BaseEntity):

    def __init__(self, node, rdf=None, parent=None):
        super(LicenseMapper, self).__init__(node, rdf, parent)

        try:
            self.rdf.parse('https://www.dcat-ap.de/def/licenses/20210721.rdf')
        except Exception as e:
            self.rdf.parse(abs_file_path('iso2dcat/data/20210721.rdf'))

        self.mapping = {}

        result = self.rdf.query(MAPPING)

        for res in result:
            self.mapping[str(res[0])] = str(res[1])


def register_licensemapper():
    license_mapper = LicenseMapper(None)
    component.provideUtility(license_mapper, ILicenseMapper)
    return license_mapper


def main():
    mapper = LicenseMapper(None)


if __name__ == "__main__":
    main()
