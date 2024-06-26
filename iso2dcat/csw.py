# -*- coding: utf-8 -*-
import io
from pathlib import Path

from lxml import etree, objectify
from owslib.csw import CatalogueServiceWeb
from owslib.fes import PropertyIsLike
from rdflib import Graph, ConjunctiveGraph

from iso2dcat.dcat import DCAT
from iso2dcat.entities.base import BaseEntity
from iso2dcat.exceptions import EntityFailed
from iso2dcat.utils import print_error
from more_itertools import chunked


class CSWProcessor(BaseEntity):
    count = 0

    _stat_title = 'Processing statistics'
    _stat_desc = """Number of processed datasets,
and how many were DCAT compatible ("good") or not "bad".
Even if a ISO dataset is DCAT compatible it may have flaws, so please look further down."""

    _stat_uuid = False

    def __init__(self):
        super(CSWProcessor, self).__init__(None, ConjunctiveGraph())
        if self.cfg.CSW_URI:
            self.csw = CatalogueServiceWeb(self.cfg.CSW_URI)
        else:
            self.logger.error('No Uri provided, make sure you use File Mode')
            self.csw = None
        # Important to set the namespaces only once!
        self.set_namespaces()

        self.inc('Bad', increment=0)

    def get_constraint(self):

        return PropertyIsLike(propertyname='apiso:subject', literal='opendata')

    def get_records(self):
        self.logger.info(self.cfg.FROM_DISK)

        if self.cfg.FROM_DISK:
            batch_start = 0
            files = Path(self.cfg.CSW_PATH).glob('*.xml')
            batch = {}
            for record_file_names in chunked(files, self.cfg.BATCH_COUNT):
                batch = {}
                for record_file_name in record_file_names:
                    with open(record_file_name, 'rb') as rf:
                        batch[record_file_name] = rf.read()
                        self.inc('Available', no_uuid=True)
                yield batch
                batch_start += self.cfg.BATCH_COUNT
                if batch_start >= self.cfg.TOTAL_COUNT_LIMIT:
                    break
            return

        batch_start = 0
        while True:
            self.csw.getrecords2(
                constraints=[self.get_constraint()],
                startposition=batch_start + 1, # +1 is important, otherwise we have one file twice
                maxrecords=self.cfg.BATCH_COUNT,
                outputschema=self.cfg.CSW_OUTPUT_SCHEMA,
                esn='full',
            )

            if len(self.csw.records) > 0:
                self.inc('Processed', increment=len(self.csw.records))

                yield {uuid: rec.xml for uuid, rec in self.csw.records.items()}
            else:
                break

            batch_start += self.cfg.BATCH_COUNT
            if batch_start >= self.cfg.TOTAL_COUNT_LIMIT:
                break

    def dispatch_records(self):
        if self.cfg.PARALLEL:
            from joblib import Parallel, delayed
            proc = Parallel(n_jobs=self.cfg.NUM_CPU, require='sharedmem')
            proc(delayed(self.handle_records)(records) for records in self.get_records())
        else:
            for records in self.get_records():
                self.handle_records(records)

    def handle_records(self, records):
        for uuid in records:
            self.count += 1
            self.logger.info(self.count)
            rec = records[uuid]

            try:
                parser = etree.XMLParser(remove_blank_text=True)
                lookup = etree.ElementNamespaceClassLookup(objectify.ObjectifyElementClassLookup())
                parser.setElementClassLookup(lookup)
                if self.cfg.SAVE_DATASETS:
                    with open('{}/{}{}.xml'.format(
                        self.cfg.CSW_PATH,
                        self.cfg.CSW_PREFIX,
                        uuid
                    ), 'wb') as outfile:
                        outfile.write(rec)

                xml_file = io.BytesIO(rec)

                node = objectify.parse(xml_file).getroot()
                dcat = DCAT(node, self.rdf)
                dcat.run()
                self.inc('Good')
            except EntityFailed:
                self.inc('Bad')
                print_error(uuid)
                self.rdf.remove((None, None, None, dcat.uuid.text))

        self.to_rdf4j(self.rdf)
        self.rdf = ConjunctiveGraph()

    def run(self):
        self.dispatch_records()
