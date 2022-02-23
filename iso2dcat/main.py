from iso2dcat.config import register_config
from iso2dcat.csw import CSWProcessor
from iso2dcat.entities.base import Base
from iso2dcat.log.log import register_logger


class Main(Base):
    def setup_components(self, args=None, env='Production'):
        # Get the configuration
        register_config(args, env=env)

        # Setup the logging facility for this measurement ID
        register_logger()
        # register_plugins()

        # Bring up the global db_access
    #    register_db_func()

    def run(self):
        self.setup_components()
        self.logger.info('iso2dcat starting')
        self.csw_proc = CSWProcessor()
        self.csw_proc.run()


if __name__ == '__main__':
    Main().run()
