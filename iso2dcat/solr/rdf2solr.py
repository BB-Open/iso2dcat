import progressbar
import pysolr
import zope
from pkan_config.config import register_config, get_config

from iso2dcat.component.interface import IIsoCfg
from iso2dcat.entities.base import BaseDCM
from iso2dcat.format_mapper import register_formatmapper
from iso2dcat.license_mapper import register_licensemapper
from iso2dcat.log.log import register_logger
from iso2dcat.namespace import register_nsmanager
from iso2dcat.rdf_database.db import register_db
from iso2dcat.solr.data import DataFormatter
from iso2dcat.statistics.stat import register_stat


class RDF2SOLR(BaseDCM):

    def __init__(self):
        super(RDF2SOLR, self).__init__()
        self.setup_components()

    def setup_components(self, args=None, env='Production', visitor=None, cfg=None):
        # Get the configuration
        if cfg:
            pass
        else:
            register_config(env=env)
            cfg = get_config()
        zope.component.provideUtility(cfg, IIsoCfg)

        # Setup the logging facility for this measurement ID
        register_logger(visitor=visitor)

        # Register the license mapper
        self.lcm = register_licensemapper()

        # Register the license mapper
        self.fm = register_formatmapper()

        self.logger.info('rdf2solr starting')
        # Register the namespace manager
        nsm = register_nsmanager()

        # Register statistics
        register_stat()
        self.stat.init(self)

        # Register RDF Database to write final results
        db = register_db()

        self.data_formatter = DataFormatter()

    def run(self, db_name=None):
        self.logger.info('Loading rdf datasets')
        data_sets = self.data_formatter.format_data_as_dict(db_name)
        self.logger.info('rdf datasets loaded')
        self.solr = pysolr.Solr(self.cfg.SOLR_URI, auth=('writer', 'Sas242!!'))
        self.logger.info('delete everything')
        self.solr.delete(q='*:*', commit=False)
        self.logger.info('writing datasets to solr')
        for key, data_set in progressbar.progressbar(data_sets.items()):
            self.solr.add(data_set)
        self.solr.commit()
        self.logger.info('datasets written to solr')
        self.logger.info('Restart solr core')
        self.solr_admin = pysolr.SolrCoreAdmin(self.cfg.SOLR_ADMIN_URI)
        self.solr_admin.reload('datasets')
        self.logger.info('Solr core restarted')

        self.logger.info('rdf2solr finished')


def main():
    rdf2solr = RDF2SOLR()
    rdf2solr.run()


if __name__ == '__main__':
    main()
