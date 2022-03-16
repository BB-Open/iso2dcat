import urllib
from urllib.parse import urlencode

from rdflib import Literal, URIRef
from rdflib.namespace import RDF, SKOS, DCTERMS

from iso2dcat.entities.base import BaseEntity, DCAT

KEYWORDS = 'gmd:identificationInfo/*/gmd:descriptiveKeywords/*[not(gmd:thesaurusName)]/gmd:keyword/gco:CharacterString'
CATEGORIES = 'gmd:identificationInfo[1]/*/gmd:topicCategory/*'
INSPIRE_THEME_LABELS = "gmd:identificationInfo/*/gmd:descriptiveKeywords/*"


class CategoryKeywordMapper(BaseEntity):

    def __init__(self, node, parent_uri):
        super().__init__(node)
        self.parent_ressource_uri = parent_uri
        self.dcat_themes = {"AGRI": ['farming', 'imageryBaseMapsEarthCover', 'inlandWaters', 'oceans'],
                            "EDUC": ['society'],
                            "ENVI": ['biota', 'climatologyMeteorologyAtmosphere', 'elevation', 'environment',
                                     'imageryBaseMapsEarthCover', 'inlandWaters', 'oceans', 'geoscientificInformation',
                                     'farming', 'utilitiesCommunication'],
                            "ENER": ['utilitiesCommunication'],
                            "TRAN": ['transportation', 'inlandWaters', 'oceans', 'structure'],
                            "TECH": ['climatologyMeteorologyAtmosphere', 'elevation', 'geoscientificInformation',
                                     'imageryBaseMapsEarthCover'],
                            "ECON": ['economy'],
                            "SOCI": ['society'],
                            "HEAL": ['health'],
                            "GOVE": ['boundaries', 'elevation', 'imageryBaseMapsEarthCover', 'location',
                                     'planningCadastre', 'utilitiesCommunication'],
                            "REGI": ['boundaries', 'location', 'planningCadastre', 'geoscientificInformation',
                                     'structure', 'imageryBaseMapsEarthCover'],
                            "JUST": ['intelligenceMilitary'],
                            "INTR": [],
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

        # if results_theme_label:
        #     self.inc('good_label')
        # else:
        #     self.inc('bad_label')

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
            for cat in self.dcat_themes:
                if keyword in self.dcat_themes[cat]:
                    self.rdf.add((URIRef(self.parent_ressource_uri), DCAT.theme, URIRef(
                        'http://publications.europa.eu/resource/authority/data-theme/' + cat)))

        self.logger.info('Set Additional Categories')
        # additional categories
        label_found = False
        for node in results_theme_label:
            label = node.xpath('gmd:thesaurusName/gmd:CI_Citation/gmd:title/gco:CharacterString[text()]', namespaces=self.nsm.namespaces)
            keywords = node.xpath('gmd:keyword/gco:CharacterString', namespaces=self.nsm.namespaces)
            if label:
                label = label[0]
                label_found = True
                label_uri = self.label_to_uri(label)
                self.rdf.add((URIRef(label_uri), RDF.type, SKOS.ConceptScheme))
                for lang in languages:
                    self.rdf.add((URIRef(label_uri), DCTERMS.title, Literal(label, lang=lang)))
                for keyword in keywords:
                    keyword_uri = self.keyword_to_uri(keyword)
                    self.rdf.add((URIRef(keyword_uri), RDF.type, SKOS.Concept))
                    self.rdf.add((URIRef(keyword_uri), SKOS.inScheme, URIRef(label_uri)))
                    self.rdf.add((URIRef(self.parent_ressource_uri), DCAT.theme, URIRef(keyword_uri)))
                    for lang in languages:
                        self.rdf.add((URIRef(keyword_uri), SKOS.prefLabel, Literal(keyword, lang=lang)))
        if label_found:
            self.inc('good_additional_cat')
        else:
            self.inc('bad_additional_cat')
        return self.rdf

    def label_to_uri(self, label):
        # todo: is there a good mapping of uris?
        uri = self.base_uri + '#skos_ConceptScheme_' + urllib.parse.quote(str(label))
        return uri

    def keyword_to_uri(self, keyword):
        # todo: is there a good mapping of uris or better generation?
        uri = self.base_uri + '#skos_Concept_' + urllib.parse.quote(str(keyword))
        return uri
