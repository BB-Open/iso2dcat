from zope import component

from iso2dcat.component.interface import IFormatMapper
from iso2dcat.format_mapper import FormatMapper, register_formatmapper
from tests.base import BaseTest


class TestFormatMapper(BaseTest):

    def setUp(self):
        super(TestFormatMapper, self).setUp()

    def test_format_mapper(self):
        mapper = FormatMapper(None)
        mapper.run()
        self.assertTrue(len(mapper.mapping) > 0)

    def test_registration(self):
        register_formatmapper()
        mapper = component.queryUtility(IFormatMapper)
        self.assertIsInstance(mapper, FormatMapper)
