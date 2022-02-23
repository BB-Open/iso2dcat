import io
from pprint import pprint

from owslib.csw import CatalogueServiceWeb
from lxml import etree
from lxml import objectify

from iso2dcat.component.interface import ILogger

from owslib.fes import PropertyIsLike

from iso2dcat.dcat import to_dcat
from iso2dcat.entities.base import Base
from iso2dcat.exceptions import EntityFailed
from iso2dcat.utils import print_error




class CSWProcessor(Base):

    count = 0

    def __init__(self):
        super(CSWProcessor, self).__init__()
        self.csw = CatalogueServiceWeb(self.cfg.CSW_URI)

    def get_constraint(self):
        return PropertyIsLike(propertyname='apiso:subject', literal='opendata')

    def get_records(self):

        batch_start = 0
        while True:
            self.csw.getrecords2(
                constraints=[self.get_constraint()],
                startposition=batch_start,
                maxrecords=self.cfg.BATCH_COUNT,
                outputschema=self.cfg.CSW_OUTPUT_SCHEMA,
                esn='full',
            )

            if len(self.csw.records) > 0:
                yield self.csw.records
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
            publisher = None
            try:
                parser = etree.XMLParser(remove_blank_text=True)
                lookup = etree.ElementNamespaceClassLookup(objectify.ObjectifyElementClassLookup())
                parser.setElementClassLookup(lookup)
                with open('xml/rec_{}.xml'.format(uuid),'wb') as outfile:
                    outfile.write(rec.xml)

                xml_file = io.BytesIO(rec.xml)

                node = etree.parse(xml_file)

                publisher = to_dcat(node)
            except EntityFailed:
                print_error(rec)

        #     if publisher is None:
        #         print('Error')
        #         bad += 1
        #     else:
        #         try:
        #             pub_name = publisher[0].text
        #             print(pub_name)
        #             if pub_name in histo:
        #                 histo[pub_name] += 1
        #             else:
        #                 histo[pub_name] = 1
        #
        #             good += 1
        #         except Exception as e:
        #             print('Error')
        #             bad += 1
        #
        # print('good {} bad {}'.format(good, bad))
        # pprint(histo)

    def run(self):
        self.dispatch_records()
