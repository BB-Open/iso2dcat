from zope import component

from iso2dcat.component.interface import IFormatMapper, ILicenseMapper
from iso2dcat.format_mapper import FormatMapper, register_formatmapper
from iso2dcat.license_mapper import LicenseMapper, register_licensemapper
from tests.base import BaseTest


class TestLicenseMapper(BaseTest):

    def setUp(self):
        super(TestLicenseMapper, self).setUp()

    def test_format_mapper(self):
        mapper = LicenseMapper(None)
        mapper.run()
        self.assertTrue(len(mapper.mapping) > 0)

    def test_registration(self):
        register_licensemapper()
        mapper = component.queryUtility(ILicenseMapper)
        self.assertIsInstance(mapper, LicenseMapper)
