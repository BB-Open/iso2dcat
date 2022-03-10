# -*- coding: utf-8 -*-
import json
import urllib.request

import pandas as pd
from zope import component

from iso2dcat.component.interface import IDCM
from iso2dcat.entities.base import Base


class DCM(Base):

    def __init__(self):
        self.dcm = None
        self.file_id_to_baseurl = {}
        self.id_to_baseurl = {}

    def run(self):
        dcm_file = urllib.request.urlopen(self.cfg.DCM_URI)
        # dcm_pandas = pd.read_csv(dcm_file, sep=';', index_col=0)
        # self.dcm = dcm_pandas.to_dict(orient='index')
        self.dcm = json.loads(dcm_file.read())
        publishers = self.dcm['publisher']['mapping']
        self.logger.info('Mapping publishers to Base Url')
        for pub in publishers:
            self.id_to_baseurl[pub['publisher_id']] = pub['publisher_url']
        files = self.dcm['dcm']['mapping']
        self.logger.info('Mapping Files to Base Url')
        for file in files:
            self.file_id_to_baseurl[file['fileidentifier']] = self.id_to_baseurl[file['publisher_id']]


def register_dcm():
    dcm = DCM()
    component.provideUtility(dcm, IDCM)
    return dcm
