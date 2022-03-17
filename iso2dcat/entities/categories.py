from pyrdf4j.errors import QueryFailed
from rdflib import Literal, URIRef
from rdflib.namespace import RDF, SKOS, DCTERMS

from iso2dcat.entities.base import BaseEntity, DCAT
from iso2dcat.meta_data_database import KNOWN_THESAURI, META_REPO_ID

KEYWORDS = 'gmd:identificationInfo/*/gmd:descriptiveKeywords/*[not(gmd:thesaurusName)]/gmd:keyword/gco:CharacterString'
CATEGORIES = 'gmd:identificationInfo[1]/*/gmd:topicCategory/*'
INSPIRE_THEME_LABELS = "gmd:identificationInfo/*/gmd:descriptiveKeywords/*"


class CategoryKeywordMapper(BaseEntity):
    cached_keywords = {}

    def __init__(self, node, parent_uri):
        super().__init__(node)
        self.parent_ressource_uri = parent_uri
        self.dcat_themes = [
            "AGRI", "EDUC", "ENVI", "ENER",
            "TRAN", "TECH", "ECON", "SOCI",
            "HEAL", "GOVE", "REGI", "JUST",
            "INTR"
        ]
        self.keywords_to_themes = {
            'farming': ['AGRI', 'ENVI'],
            'imageryBaseMapsEarthCover': ['AGRI', 'ENVI', 'TECH', 'GOVE', 'REGI'],
            'inlandWaters': ['AGRI', 'ENVI', 'TRAN'],
            'oceans': ['AGRI', 'ENVI', 'TRAN'],
            'society': ["EDUC", 'SOCI'],
            'biota': ["ENVI"],
            'climatologyMeteorologyAtmosphere': ['ENVI', 'TECH'],
            'elevation': ['ENVI', 'TECH', 'GOVE'],
            'environment': ['ENVI'],
            'geoscientificInformation': ['ENVI', 'TECH', 'REGI'],
            'utilitiesCommunication': ['ENVI', 'ENER', 'GOVE'],
            'transportation': ['TRAN'],
            'structure': ['TRAN', 'REGI'],
            'economy': ['ECON'],
            'health': ['HEAL'],
            'boundaries': ['GOVE', 'REGI'],
            'location': ['GOVE', 'REGI'],
            'planningCadastre': ['GOVE', 'REGI'],
            'intelligenceMilitary': ["JUST"]
        }

    def run(self):
        results_kw = self.node.xpath(KEYWORDS,
                                     namespaces=self.nsm.namespaces)
        results_cat = self.node.xpath(CATEGORIES,
                                      namespaces=self.nsm.namespaces)
        results_theme_label = self.node.xpath(INSPIRE_THEME_LABELS,
                                              namespaces=self.nsm.namespaces)

        if results_kw:
            self.inc('good_kw')
        else:
            self.inc('bad_kw')

        if results_cat:
            self.inc('good_cat')
        else:
            self.inc('bad_cat')

        languages = self.get_languages()

        # create keywords as keyword
        self.logger.info('Set Keywords')
        for keyword in results_kw:
            for lang in languages:
                self.rdf.add((URIRef(self.parent_ressource_uri), DCAT.keyword, Literal(keyword, lang=lang)))
                if str(keyword).upper() in self.dcat_themes:
                    self.rdf.add((URIRef(self.parent_ressource_uri), DCAT.theme, URIRef(
                        'http://publications.europa.eu/resource/authority/data-theme/' + str(keyword).upper())))
        # create categories
        self.logger.info('Set Default Categories')
        for keyword in results_cat:
            if keyword in self.keywords_to_themes:
                cats = self.keywords_to_themes[keyword]
                for cat in cats:
                    self.rdf.add((URIRef(self.parent_ressource_uri), DCAT.theme, URIRef(
                        'http://publications.europa.eu/resource/authority/data-theme/' + cat)))

        self.logger.info('Set Additional Categories')
        # additional categories
        additional_cat_found = False
        for node in results_theme_label:
            label = node.xpath('gmd:thesaurusName/gmd:CI_Citation/gmd:title/gco:CharacterString[text()]',
                               namespaces=self.nsm.namespaces)
            keywords = node.xpath('gmd:keyword/gco:CharacterString', namespaces=self.nsm.namespaces)
            if label:
                label = label[0]

                label_uri = self.label_to_uri(label)
                if not label_uri:
                    self.logger.error('Missing Data for Thesauri ' + label)
                    continue
                for keyword in keywords:
                    keyword_uri = self.keyword_to_uri(keyword)
                    if not keyword_uri:
                        self.logger.error('Keyword not found in store: ' + keyword)
                        continue
                    additional_cat_found = True
                    self.logger.debug('Additional Categorie found for: ' + keyword)
                    self.rdf.add((URIRef(label_uri), RDF.type, SKOS.ConceptScheme))
                    self.rdf.add((URIRef(keyword_uri), RDF.type, SKOS.Concept))
                    self.rdf.add((URIRef(keyword_uri), SKOS.inScheme, URIRef(label_uri)))
                    self.rdf.add((URIRef(self.parent_ressource_uri), DCAT.theme, URIRef(keyword_uri)))
                    for lang in languages:
                        self.rdf.add((URIRef(keyword_uri), SKOS.prefLabel, Literal(keyword, lang=lang)))
                        self.rdf.add((URIRef(label_uri), DCTERMS.title, Literal(label, lang=lang)))
        if additional_cat_found:
            self.inc('good_additional_cat')
        else:
            self.inc('bad_additional_cat')
        return self.rdf

    def label_to_uri(self, label):
        if label in KNOWN_THESAURI:
            return KNOWN_THESAURI[label]['base']
        else:
            return None

    def keyword_to_uri(self, keyword):
        # todo: why is there a problem with utf-8 character?
        if keyword in self.cached_keywords:
            return self.cached_keywords[keyword]
        query = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT ?s WHERE { ?s skos:prefLabel ?label FILTER (lcase(str(?label)) = '""" + str(keyword).lower().encode(
            'utf-8').decode("iso-8859-1") + """').}"""
        try:
            res = self.rdf4j.query_repository(META_REPO_ID, query)
        except QueryFailed:
            self.logger.error('Query failed')
            self.logger.error(query)
            uri = None
        else:
            if res['results']['bindings']:
                uri = res['results']['bindings'][0]['s']['value']
            else:
                uri = None
        self.cached_keywords[keyword] = uri
        return uri