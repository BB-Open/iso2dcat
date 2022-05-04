import zope
from pyrdf4j.errors import TerminatingError, CannotStartTransaction
from zope import component

from iso2dcat.component.interface import IRDFDatabase
from iso2dcat.entities.base import Base

from pyrdf4j.rdf4j import RDF4J
from requests.auth import HTTPBasicAuth


@zope.interface.implementer(IRDFDatabase)
class RDFDatabase(Base):
    """
    RDF Database
    """

    def __init__(self):
        self.rdf4j = RDF4J(rdf4j_base=self.cfg.RDF4J_BASE)
        self.auth = HTTPBasicAuth(self.cfg.ADMIN_USER, self.cfg.ADMIN_PASS)

    def insert_data(self, data, content_type):
        # todo: Better Error handling
        if isinstance(data, str):
            data = data.encode('utf-8')

        try:
            return self.rdf4j.add_data_to_repo(
                self.cfg.WRITE_TO,
                data,
                content_type,
                auth=self.auth
            )
        except TerminatingError as e:
            self.logger.error('Could not write data cause of TerminatingError.')
            self.logger.error(data)
            self.logger.error(e.args)
        except CannotStartTransaction as e:
            self.logger.error('Could not write data cause of CannotStartTransactionError.')
            self.logger.error(data)
            self.logger.error(e.args)

    def query_repository(self, repo_id, query):
        return self.rdf4j.query_repository(repo_id, query, self.auth)


def register_db():
    db = component.queryUtility(IRDFDatabase)
    if db is not None:
        return db

    db = RDFDatabase()
    component.provideUtility(db, IRDFDatabase)
    return db
