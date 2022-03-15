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
        self._file_id_to_baseurl = {}
        self._id_to_baseurl = {}

    def run(self):
        dcm_file = urllib.request.urlopen(self.cfg.DCM_URI)
        # dcm_pandas = pd.read_csv(dcm_file, sep=';', index_col=0)
        # self.dcm = dcm_pandas.to_dict(orient='index')
        self.dcm = json.loads(dcm_file.read())
        publishers = self.dcm['publisher']['mapping']
        self.logger.info('Mapping publishers to Base Url')
        for pub in publishers:
            self._id_to_baseurl[pub['publisher_id']] = pub['publisher_url']
        files = self.dcm['dcm']['mapping']
        self.logger.info('Mapping Files to Base Url')
        for file in files:
            self._file_id_to_baseurl[file['fileidentifier']] = self._id_to_baseurl[file['publisher_id']]

    def file_id_to_baseurl(self, file_id, return_fallback=False):
        try:
            res = self._file_id_to_baseurl[file_id]
        except KeyError:
            if return_fallback:
                res = self.cfg.FALLBACK_CATALOG_URL
            else:
                res = None
            self.logger.error('ISO-Dataset ID "{}" not in DCM'.format(file_id))
        return res


def register_dcm():
    dcm = DCM()
    component.provideUtility(dcm, IDCM)
    return dcm
