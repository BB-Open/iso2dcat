# -*- coding: utf-8 -*-
import urllib.request

import pandas as pd
from zope import component

from iso2dcat.component.interface import IDCM
from iso2dcat.entities.base import Base


class DCM(Base):

    def __init__(self):
        self.dcm = None

    def run(self):
        dcm_file = urllib.request.urlopen(self.cfg.DCM_URI)
        dcm_pandas = pd.read_csv(dcm_file, sep=';', index_col=0)
        self.dcm = dcm_pandas.to_dict(orient='index')
        pass


def register_dcm():
    dcm = DCM()
    component.provideUtility(dcm, IDCM)
    return dcm
