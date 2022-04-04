from zope import component

from iso2dcat.component.interface import IFormatMapper
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


class FormatMapper(BaseEntity):

    def __init__(self, node, rdf=None, parent=None):
        super(FormatMapper, self).__init__(node, rdf, parent)

        try:
            self.rdf.parse('https://op.europa.eu/o/opportal-service/euvoc-download-handler?cellarURI=http%3A%2F%2Fpublications.europa.eu%2Fresource%2Fcellar%2F5333010f-a579-11ec-83e1-01aa75ed71a1.0001.04%2FDOC_1&fileName=filetypes-skos.rdf')
        except Exception as e:
            self.rdf.parse(abs_file_path('iso2dcat/data/filetypes-skos.rdf'))

        self.mapping = {}

        result = self.rdf.query(MAPPING)

        for res in result:
            self.mapping[str(res[0])] = str(res[1])


def register_formatmapper():
    format_mapper = FormatMapper(None)
    component.provideUtility(format_mapper, IFormatMapper)
    return  format_mapper


def main():
    mapper = FormatMapper(None)


if __name__ == "__main__":
    main()
