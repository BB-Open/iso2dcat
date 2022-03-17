# -*- coding: utf-8 -*-

import zope
from zope import component

from iso2dcat.component.interface import IStat, ICfg
from iso2dcat.config import register_config
from iso2dcat.csw import CSWProcessor
from iso2dcat.dcat import CatalogBuilder
from iso2dcat.dcm import register_dcm
from iso2dcat.entities.base import Base
from iso2dcat.entities.catalog import Catalog
from iso2dcat.entities.categories import CategoryKeywordMapper
from iso2dcat.entities.contactpoint import ContactPoint
from iso2dcat.entities.dates import DateMapper
from iso2dcat.entities.hierarchy import Hirarchy
from iso2dcat.entities.languagemapper import register_languagemapper
from iso2dcat.entities.publisher import Publisher, Contributor, Maintainer
from iso2dcat.log.log import register_logger
from iso2dcat.namespace import register_nsmanager
from iso2dcat.rdf_database.db import register_db
from iso2dcat.statistics.stat import register_stat


class Main(Base):
    db = None
    csw_proc = None
    dcm = None
    nsm = None

    def setup_components(self, args=None, env='Production', visitor=None, cfg=None):
        # Get the configuration
        if cfg:
            zope.component.provideUtility(cfg, ICfg)
        else:
            register_config(args, env=env)

        # Setup the logging facility for this measurement ID
        register_logger(visitor=visitor)

        # Register the namespace manager
        self.nsm = register_nsmanager()

        # Register statistics
        register_stat()

        # Register RDF Database to write final results
        self.db = register_db()

        # Register the DCM-Interface
        self.dcm = register_dcm()

        # register language mapper
        self.language_mapper = register_languagemapper()

    def run(self, visitor=None, cfg=None):
        self.setup_components(visitor=visitor, cfg=cfg)
        self.logger.info('iso2dcat starting')

        self.logger.info('loading Languages')
        self.language_mapper.run()
        self.logger.info('Languages file loaded')

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
        for klass in [CSWProcessor, Catalog, Publisher, ContactPoint, Hirarchy, Contributor, Maintainer,
                      CategoryKeywordMapper, DateMapper]:
            for line in stat.get_stats(klass):
                self.logger.info(line)

        # todo: RDF2Solr should be in scheduler, part of flask package
        # self.logger.info('RDF2Solr')
        # try:
        #     self.rdf2solr = RDF2SOLR()
        #     self.rdf2solr.run()
        # except Exception:
        #     pass
        # pprint.pprint(self.rdf2solr.test1().docs)
        self.logger.info('iso2dcat finished')


if __name__ == '__main__':
    Main().run()
