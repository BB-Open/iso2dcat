from pkan_config.config import register_config
from pyrdf4j.rdf4j import RDF4J
from requests.auth import HTTPBasicAuth

from iso2dcat.entities.base import Base
from iso2dcat.log.log import register_logger

META_REPO_ID = 'iso_dcat_meta_repo'
KNOWN_THESAURI = {
    'GEMET - INSPIRE themes, version 1.0': {'source': 'https://www.eionet.europa.eu/gemet/latest/gemet.rdf.gz',
                                            'base': 'http://www.eionet.europa.eu/gemet/',
                                            'format': 'application/rdf+xml'}
}

class Main(Base):

    def __init__(self, env='Production', args=None):
        register_config(env=env)
        register_logger()
        self.rdf4j = RDF4J(rdf4j_base=self.cfg.RDF4J_BASE)
        self.auth = HTTPBasicAuth(self.cfg.ADMIN_USER, self.cfg.ADMIN_PASS)

    def run(self):
        self.logger.info('Create Database')
        self.rdf4j.create_repository(META_REPO_ID, overwrite=False, accept_existing=True, auth=self.auth, repo_type='native')
        for thesaurus in KNOWN_THESAURI:
            source = KNOWN_THESAURI[thesaurus]['source']
            format = KNOWN_THESAURI[thesaurus]['format']
            self.logger.info('Load ' + thesaurus)
            self.rdf4j.bulk_load_from_uri(META_REPO_ID, source, content_type=format, clear_repository=False, auth=self.auth)
            self.logger.info('Loaded')



if __name__ == '__main__':
    Main().run()
