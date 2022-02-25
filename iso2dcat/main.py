# -*- coding: utf-8 -*-
from iso2dcat.config import register_config
from iso2dcat.csw import CSWProcessor
from iso2dcat.dcm import register_dcm
from iso2dcat.entities.base import Base
from iso2dcat.entities.catalog import Catalog
from iso2dcat.entities.contactpoint import ContactPoint
from iso2dcat.entities.publisher import Publisher
from iso2dcat.log.log import register_logger


class Main(Base):

    dcm = None
    csw_proc = None

    def setup_components(self, args=None, env='Production'):
        # Get the configuration
        register_config(args, env=env)

        # Setup the logging facility for this measurement ID
        register_logger()
        # register_plugins()

        self.dcm = register_dcm()
        # Bring up the global db_access
    #    register_db_func()

    def run(self):
        self.setup_components()
        self.logger.info('iso2dcat starting')

        self.logger.info('loading DCM file')
        self.dcm.run()
        self.logger.info('DCM file loaded')

        self.logger.info('processing ISO files')
        self.csw_proc = CSWProcessor()
        self.csw_proc.run()
        self.logger.info('ISO files processed')

        self.logger.info('iso2dcat finished')
        self.logger.info('iso2dcat statistics')
        for klass in [Catalog, Publisher, ContactPoint] :
            klass.show_stats()


if __name__ == '__main__':
    Main().run()
