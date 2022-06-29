from rdflib import Literal
from rdflib.namespace import RDF, SKOS, DCTERMS
from zope import component

from iso2dcat.entities.base import BaseEntity
from iso2dcat.namespace import DCAT
from iso2dcat.thesauri_mapper import KNOWN_THESAURI

KEYWORDS = 'gmd:identificationInfo/*/gmd:descriptiveKeywords/*/gmd:keyword/gco:CharacterString'
CATEGORIES = 'gmd:identificationInfo[1]/*/gmd:topicCategory/*'
INSPIRE_THEME_LABELS = "gmd:identificationInfo/*/gmd:descriptiveKeywords/*"


class CategoryKeywordMapper(BaseEntity):

    _stat_title = 'Categories and Keywords'
    _stat_desc = """Convert all gmd:keyword to dcat:keyword
Convert gmd:topicCategory to standard dcat:theme
Convert gmd:descriptiveKeywords to additional dcat:theme for known thesauri

Category Mapping iso to dcat:
'farming': ['AGRI', 'ENVI']
'imageryBaseMapsEarthCover': ['AGRI', 'ENVI', 'TECH', 'GOVE', 'REGI']
'inlandWaters': ['AGRI', 'ENVI', 'TRAN']
'oceans': ['AGRI', 'ENVI', 'TRAN']
'society': ['EDUC', 'SOCI']
'biota': ['ENVI']
'climatologyMeteorologyAtmosphere': ['ENVI', 'TECH']
'elevation': ['ENVI', 'TECH', 'GOVE']
'environment': ['ENVI']
'geoscientificInformation': ['ENVI', 'TECH', 'REGI']
'utilitiesCommunication': ['ENVI', 'ENER', 'GOVE']
'transportation': ['TRAN']
'structure': ['TRAN', 'REGI']
'economy': ['ECON']
'health': ['HEAL']
'boundaries': ['GOVE', 'REGI']
'location': ['GOVE', 'REGI']
'planningCadastre': ['GOVE', 'REGI']
'intelligenceMilitary': ['JUST']

Currently known thesauri:
 * GEMET - INSPIRE themes, version 1.0

Details:
Good: Keyword or topic Category found
Bad: No Keyword or topic Category found
good_kw: Keyword found and converted
bad_kw: No Keyword found
good_cat: topic Category found and converted
bad_cat: No topic Category found
good_additional_cat: Keywords of known Thesauri found and converted
bad_additional_cat: No Keywords of known Thesauri found and converted
"""

    def __init__(self, node, rdf, parent_uri):
        super().__init__(node, rdf, parent_uri)
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
        self.inc('Processed')
        results_kw = self.node.xpath(KEYWORDS,
                                     namespaces=self.nsm.namespaces)
        results_cat = self.node.xpath(CATEGORIES,
                                      namespaces=self.nsm.namespaces)
        results_theme_label = self.node.xpath(INSPIRE_THEME_LABELS,
                                              namespaces=self.nsm.namespaces)

        if results_kw or results_cat:
            self.inc('Good')
        else:
            self.inc('Bad')

        if results_kw:
            self.inc('good_kw')
        else:
            self.inc('bad_kw')

        if results_cat:
            self.inc('good_cat')
        else:
            self.inc('bad_cat')

        languages = self.get_languages()

        parent_uri_ref = self.make_uri_ref(self.parent_ressource_uri)

        # create keywords as keyword
#        self.logger.info('Set Keywords')
        for keyword in results_kw:
            for lang in languages:
                self.add_tripel(
                    parent_uri_ref,
                    DCAT.keyword,
                    Literal(keyword, lang=lang)
                )
                if str(keyword).upper() in self.dcat_themes:
                    self.add_tripel(
                        parent_uri_ref,
                        DCAT.theme,
                        self.make_uri_ref(
                            'http://publications.europa.eu/resource/authority/data-theme/'
                            + str(keyword).upper()
                        )
                    )
        # create categories
#        self.logger.info('Set Default Categories')
        for keyword in results_cat:
            if keyword in self.keywords_to_themes:
                cats = self.keywords_to_themes[keyword]
                for cat in cats:
                    self.add_tripel(parent_uri_ref, DCAT.theme, self.make_uri_ref(
                        'http://publications.europa.eu/resource/authority/data-theme/' + cat))

#        self.logger.info('Set Additional Categories')
        # additional categories
        # todo: Improve additional categories
        # todo: Make Themes as dictionary
        additional_cat_found = False
        for node in results_theme_label:
            label = node.xpath(
                'gmd:thesaurusName/gmd:CI_Citation/gmd:title/gco:CharacterString[text()]',
                namespaces=self.nsm.namespaces
            )
            keywords = node.xpath(
                'gmd:keyword/gco:CharacterString',
                namespaces=self.nsm.namespaces
            )
            if label:
                label = label[0]

                mapper = self.get_mapper(label)

                if not mapper:
                    self.logger.warning('Missing Data for Thesauri ' + label)
                    continue
                mapper_uri_ref = self.make_uri_ref(mapper.base)
                for keyword in keywords:
                    keyword_uris = mapper.keyword_to_uri(keyword)
                    if not keyword_uris:
                        self.logger.warning('Keyword not found in store: ' + keyword)
                        continue
                    additional_cat_found = True
                    for keyword_uri in keyword_uris:
                        self.logger.debug('Additional Categorie found for: ' + keyword)
                        self.add_tripel(
                            mapper_uri_ref,
                            RDF.type,
                            SKOS.ConceptScheme
                        )
                        self.add_tripel(
                            keyword_uri,
                            RDF.type,
                            SKOS.Concept
                        )
                        self.add_tripel(
                            keyword_uri,
                            SKOS.inScheme,
                            mapper_uri_ref
                        )
                        self.add_tripel(
                            parent_uri_ref,
                            DCAT.theme,
                            keyword_uri
                        )
                        for lang in languages:
                            self.add_tripel(
                                keyword_uri,
                                SKOS.prefLabel,
                                Literal(keyword, lang=lang)
                            )
                            self.add_tripel(
                                mapper_uri_ref,
                                DCTERMS.title,
                                Literal(label, lang=lang)
                            )
        if additional_cat_found:
            self.inc('good_additional_cat')
        else:
            self.inc('bad_additional_cat')

    def get_mapper(self, label):
        if label in KNOWN_THESAURI:
            return component.queryUtility(KNOWN_THESAURI[label])
        else:
            return None
