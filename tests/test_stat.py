from zope import component

from iso2dcat.component.interface import IStat
from iso2dcat.entities.dataset import DcatDataset
from iso2dcat.statistics.stat import Stat
from tests.base import BaseTest


class TestStat(BaseTest):

    def setUp(self):
        super(TestStat, self).setUp()
        self.stat = Stat()

    def test_get_stat(self):
        self._stat_count = True
        self._stat_uuid = False
        self._stat_title = 'Test'
        self._stat_desc = 'Description'
        self.stat.inc(self, 'test', no_uuid=True)
        self.stat.inc(self, 'test', no_uuid=True)
        self.stat.inc(self, 'test_again', no_uuid=True)

        res = '\n'.join(self.stat.get_stats(TestStat))
        self.assertTrue('test' in res)
        self.assertTrue('test_again' in res)
        self.assertTrue('1' in res)
        self.assertTrue('2' in res)
        self.assertTrue(self._stat_title in res)
        self.assertTrue(self._stat_desc in res)

        res = '\n'.join(self.stat.get_stats(DcatDataset))
        self.assertTrue(res == '')
