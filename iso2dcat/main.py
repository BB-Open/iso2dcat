# -*- coding: utf-8 -*-

import zope
from pkan_config.config import register_config, get_config
from zope import component

from iso2dcat.component.interface import IStat, IIsoCfg
from iso2dcat.csw import CSWProcessor
from iso2dcat.dcat import CatalogBuilder
from iso2dcat.dcm import register_dcm
from iso2dcat.entities.base import Base, BaseEntity
from iso2dcat.entities.catalog import Catalog
from iso2dcat.entities.categories import CategoryKeywordMapper
from iso2dcat.entities.contactpoint import ContactPoint
from iso2dcat.entities.dataservice import DcatDataService
from iso2dcat.entities.dates import DateMapper
from iso2dcat.entities.distribution import Distribution
from iso2dcat.entities.hierarchy import Hierarchy
from iso2dcat.entities.foafdocuments import FoafDocuments
from iso2dcat.entities.languagemapper import register_languagemapper, LanguageMapper
from iso2dcat.entities.licenses import License
from iso2dcat.entities.locationboundingbox import LocationBoundingbox
from iso2dcat.entities.periodicity import AccrualPeriodicity
from iso2dcat.entities.priority import InqbusPriority
from iso2dcat.entities.provenance import ProvenanceStatement
from iso2dcat.entities.publisher import Publisher, Contributor, Maintainer
from iso2dcat.entities.rightstatement import RightsStatement
from iso2dcat.log.log import register_logger
from iso2dcat.namespace import register_nsmanager
from iso2dcat.rdf_database.db import register_db
from iso2dcat.statistics.stat import register_stat
from iso2dcat.thesauri_mapper import register_thesauri


class Main(Base):
    db = None
    csw_proc = None
    dcm = None
    nsm = None

    def setup_components(self, args=None, env='Production', cfg=None, visitor=None):
        # Get the local configuration
        if cfg:
            pass
        else:
            register_config(env=env)
            cfg = get_config()
        zope.component.provideUtility(cfg, IIsoCfg)

        # Get the global configuration
        # register_config(config_file_dir='/etc/pkan/iso2dcat', env=env, interface=IGlobalCfg)

        # Setup the logging facility for this measurement ID
        register_logger(visitor=visitor)

        self.logger.info('iso2dcat starting')

        # Register the namespace manager
        self.nsm = register_nsmanager()

        # Register statistics
        register_stat()

        # register Thesauri
        register_thesauri()

        # Register RDF Database to write final results
        self.db = register_db()

        # Register the DCM-Interface
        self.dcm = register_dcm()

        # register language mapper
        self.logger.info('loading Languages')
        self.language_mapper = register_languagemapper()
        self.logger.info('Languages file loaded')

    def run(self, visitor=None, cfg=None):
        self.setup_components(visitor=visitor, cfg=cfg)

        self.logger.info('loading DCM file')
        self.dcm.run()
        self.logger.info('DCM file loaded')

        self.logger.info('Build Catalogs')
        self.catalog_builder = CatalogBuilder()
        self.catalog_builder.run()
        self.logger.info('Build Catalogs finished')

        self.logger.info('processing ISO files')
        self.csw_proc = CSWProcessor()
        self.csw_proc.run()
        self.logger.info('ISO files processed')

        self.logger.info('iso2dcat statistics')
        stat = component.queryUtility(IStat)
        lines = []
        for klass in [CSWProcessor, Catalog, Publisher, ContactPoint, Hierarchy, Contributor, Maintainer,
                      CategoryKeywordMapper, DateMapper, LocationBoundingbox, Distribution, DcatDataService,
                      AccrualPeriodicity, FoafDocuments, RightsStatement, ProvenanceStatement, LanguageMapper,
                      InqbusPriority, License]:
            for line in stat.get_stats(klass):
                lines.append(line)

        for line in lines:
            self.logger.info(line)
        for line in lines:
            print(line)


        # todo: RDF2Solr should be in scheduler, part of flask package
        # self.logger.info('RDF2Solr')
        # try:
        #     self.rdf2solr = RDF2SOLR()
        #     self.rdf2solr.run()
        # except Exception:
        #     pass
        # pprint.pprint(self.rdf2solr.test1().docs)
        self.logger.info('iso2dcat finished')


ALL_PREFIXES = [
    'dct: <http://purl.org/dc/terms/>',
    'skos: <http://www.w3.org/2004/02/skos/core#>',
    'rdfs: <http://www.w3.org/2000/01/rdf-schema#>',
    'dcat: <http://www.w3.org/ns/dcat#>',
    'dcatde: <http://dcat-ap.de/def/dcatde/>',
    'foaf: <http://xmlns.com/foaf/0.1/>',
    'rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>',
    'adms: <http://www.w3.org/ns/adms#>',
    'owl: <http://www.w3.org/2002/07/owl>',
    'schema: <http://schema.org/>',
    'spdx: <http://spdx.org/rdf/terms#>',
    'xsd: <http://www.w3.org/2001/XMLSchema#>',
    'vcard: <http://www.w3.org/2006/vcard/ns#>',
]

if __name__ == '__main__':
    m = Main()
    m.run()
    # m.setup_components()
    # prefixes = 'PREFIX ' + '\nPREFIX '.join(ALL_PREFIXES)
    #
    # obj_id = 'https://geobasis-bb.de#dcat_DataService_ea942e1e-8d54-4f9a-963a-764070c455ca'
    #
    # query = prefixes + "\nCONSTRUCT { ?s ?p ?o } WHERE {?s ?p ?o. FILTER(?s = <" \
    #         + obj_id + "> || ?p = <" + obj_id + "> || ?o = <" + obj_id + "> )}"
    # data = m.db.rdf4j.get_turtle_from_query(m.cfg.WRITE_TO, query, auth=m.db.auth)
    #
    # with open('test.ttl', 'bw') as f:
    #     f.write(data)
