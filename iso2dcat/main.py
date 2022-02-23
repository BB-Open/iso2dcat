from iso2dcat.config import register_config
from iso2dcat.log.log import register_logger


def setup_components(args=None, env='Production'):
    # Get the configuration
    register_config(args, env=env)

    # Setup the logging facility for this measurement ID
    register_logger()
    # register_plugins()

    # Bring up the global db_access
#    register_db_func()


def main():
    setup_components()


if __name__ == '__main__':
    main()
