from pathlib import Path

from iso2dcat.path_utils import abs_file_path
from tests.base import BaseTest


class TestUtils(BaseTest):

    def test_abs_path(self):
        res = abs_file_path('/home')

        self.assertTrue(Path('/home') == res)
