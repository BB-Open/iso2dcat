import pickle

from rdflib import Graph, Namespace
from rdflib.plugins.sparql import prepareQuery
from zope import component

from iso2dcat.component.interface import ILanguageMapper
from iso2dcat.entities.base import BaseStat
from iso2dcat.path_utils import abs_file_path

LANGUAGE_SOURCE_FILE = abs_file_path('iso2dcat/data/languages.rdf')
LANGUAGE_MAPPER_PICKLE_FILE = abs_file_path('iso2dcat/data/language_mapper.pickle')


class LanguageMapper(BaseStat):

    _stat_uuid = True
    _stat_count = True
    _stat_title = "LanguageMapper"
    _stat_desc = ""

    def __init__(self):
        super(LanguageMapper, self).__init__()
        self._old_to_new_style = {}
        self._old_to_subject = {}
        self._subject_to_new = {}

    def run(self):
        file = LANGUAGE_SOURCE_FILE
        g = Graph()
        g.parse(str(file))

        language_query = """
        SELECT DISTINCT ?s ?p ?o
        WHERE {
            ?s ?p ?o
        }"""

        # qres = g.query(knows_query)
        # for row in qres:
        #     print(f"{row.s} {row.p} {row.o}")

        language_query = """
                SELECT DISTINCT ?s ?o ?norm
                WHERE {
                    ?s ?p ?x .
                    ?x dc:source ?norm .
                    ?x <http://publications.europa.eu/ontology/authority/legacy-code> ?o .
                }"""
        query = prepareQuery(
            language_query,
            initNs={"euvoc": Namespace('http://publications.europa.eu/ontology/euvoc#'),
                    "dc": Namespace('http://purl.org/dc/elements/1.1/')}
        )
        qres = g.query(query)
        for row in qres:
            if len(row.o) == 3:
                self._old_to_subject[row.o.lower()] = row.s.toPython()
            elif len(row.o) == 2:
                value = row.o.lower()
                uri = row.s.toPython()
                if row.norm.toPython() == 'iso-639-1':
                    if uri in self._subject_to_new:
                        if value in self._subject_to_new[uri]:
                            pass
                        else:
                            self._subject_to_new[uri].append(value)
                    else:
                        self._subject_to_new[uri] = [value]
                else:
                    # we just wand iso-Norm as 2 letter Norm
                    pass

        for old, uri in self._old_to_subject.items():
            if uri in self._subject_to_new:
                self._old_to_new_style[old] = self._subject_to_new[uri]

    def convert(self, codes, obj):
        self.inc_obj('Processed', obj)
        res = []
        for code in codes:
            if code in self._old_to_new_style:
                for new_code in self._old_to_new_style[code]:
                    if new_code not in res:
                        self.inc_obj(new_code, obj)
                        res.append(new_code)
            else:
                res.append(code)
                self.inc_obj(code, obj)
        self.inc_obj('Good', obj)
        return res

    def inc_obj(self, stat, obj):
        if obj:
            self.stat.inc(obj, stat, cls_name=self.__class__.__name__)


def register_languagemapper():
    try:
        with open(LANGUAGE_MAPPER_PICKLE_FILE, 'rb') as in_file:
            language_mapper = pickle.load(in_file)
    except FileNotFoundError:
        language_mapper = LanguageMapper()
        language_mapper.run()
        with open(LANGUAGE_MAPPER_PICKLE_FILE, 'wb') as out_file:
            pickle.dump(language_mapper, out_file)
    component.provideUtility(language_mapper, ILanguageMapper)
    return language_mapper

def unregister_languagemapper():
    component.provideUtility(None, ILanguageMapper)
