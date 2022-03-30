# -*- coding: utf-8 -*-
from logging import ERROR, log
from pathlib import Path

import iso2dcat


def dir_not_found_hint(path_str):
    abs_path = Path(path_str).absolute()

    log(ERROR,
        """To create the missing directory please do\n
           $mkdir {path}
        """.format(path=abs_path))


def abs_file_path(*file_path):
    """
    Make a relative file_path absolute in respect to the projekt directory.
    Absolute path wil not be changed
    """
    path = Path(*file_path)
    if path.is_absolute():
        return path
    return Path(iso2dcat.__file__).parent.parent / path
