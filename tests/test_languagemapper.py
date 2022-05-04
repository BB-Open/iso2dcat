from iso2dcat.entities.languagemapper import LanguageMapper
from tests.base import BaseTest


class TestLanguageMapper(BaseTest):

    def setUp(self):
        super(TestLanguageMapper, self).setUp()
        self.language_mapper = LanguageMapper()

    def test_run_and_convert(self):
        self.language_mapper.run()
        self.assertTrue(len(self.language_mapper._old_to_new_style) > 0)
        self.assertTrue(len(self.language_mapper._old_to_subject) > 0)
        self.assertTrue(len(self.language_mapper._subject_to_new) > 0)

        res = self.language_mapper.convert(['ger'], None)
        self.assertTrue(res == ['de'])
        res = self.language_mapper.convert(['hallo'], None)
        self.assertTrue(res == ['hallo'])
