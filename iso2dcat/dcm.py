# -*- coding: utf-8 -*-
import json
import urllib.request

from zope import component

from iso2dcat.component.interface import IDCM
from iso2dcat.entities.base import Base
from iso2dcat.path_utils import abs_file_path


class DCM(Base):

    def __init__(self):
        self.dcm = None
        self._file_id_to_baseurl = {}
        self._id_to_baseurl = {}
        self._id_to_priority = {}
        self.cache_file = abs_file_path('iso2dcat/data/dcm.json')

    def run(self):
        if self.cfg.DCM_URI == '' or self.cfg.DCM_URI is None:
            self.logger.warning('No DCM file')
            return
        try:
            self.logger.info('Update cache')
            url_dcm_file = urllib.request.urlopen(self.cfg.DCM_URI)
            data = url_dcm_file.read()
            if data:
                output_file = open(self.cache_file, mode='wb')
                output_file.write(data)
                output_file.close()
                url_dcm_file.close()
            else:
                self.logger.info('Could not read source, read cache without update.')
        except Exception:
            self.logger.info('Could not read source, read cache without update.')
        dcm_file = open(self.cache_file, mode='rb')
        self.dcm = json.loads(dcm_file.read())
        publishers = self.dcm['publisher']['mapping']
        self.logger.info('Mapping publishers to Base Url')
        for pub in publishers:
            if 'publisher_id' in pub and 'publisher_url' in pub:
                self._id_to_baseurl[pub['publisher_id']] = pub['publisher_url']
        files = self.dcm['dcm']['mapping']
        self.logger.info('Mapping Files to Base Url')
        for file in files:
            if 'publisher_id' in file and 'fileidentifier' in file:
                self._file_id_to_baseurl[file['fileidentifier']] = self._id_to_baseurl[
                    file['publisher_id']
                ]
            if 'fileidentifier' in file and 'priority' in file:
                self._id_to_priority[file['fileidentifier']] = file['priority']
        dcm_file.close()

    def file_id_to_baseurl(self, file_id):
        try:
            res = self._file_id_to_baseurl[file_id]
        except KeyError:
            res = self.cfg.FALLBACK_URL
            self.logger.warning('ISO-Dataset ID "{}" not in DCM'.format(file_id))
        return res

    def id_to_priority(self, uuid):
        """
        Get the priority of the dataset or dataservice from the DCM.
        """
        priority = self._id_to_priority[uuid]
        return priority


def register_dcm():
    dcm = component.queryUtility(IDCM)
    if dcm is not None:
        return dcm
    dcm = DCM()
    component.provideUtility(dcm, IDCM)
    return dcm

def unregister_dcm():
    component.provideUtility(None, IDCM)
