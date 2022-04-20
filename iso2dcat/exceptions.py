# -*- coding: utf-8 -*-
"""Iso2Dcat exceptions"""


class Iso2DcatException(BaseException):
    """
    base class of exceptions raised by ELDAmwl
    """
    return_value = None
    prod_id = None

    def __init__(self, prod_id):
        self.prod_id = prod_id


class Terminating(BaseException):
    """
    Marker Exception mixing for terminating Exceptions
    """


class DBErrorTerminating(Iso2DcatException):
    """
    Raised when a terminating DB problem occurs
    """


class CsvFileNotFound(Iso2DcatException):
    """
    Raised when the csv file is not found; can occur only while testing
    """


class NotFoundInStorage(Iso2DcatException):
    """
    Raised if the requested data are not found in data storage
    """

    def __init__(self, what, where):
        self.what = what
        self.where = where

    def __str__(self):
        return ('cannot find {0} for {1} '
                'in data storage'.format(self.what, self.where))


class LogPathNotExists(Iso2DcatException):
    """raised when the path for writing the log file does not exists"""


class WrongCommandLineParameter(Iso2DcatException):
    """raised when wrong command line parameters are provided"""


class EntityFailed(Exception):
    """"
    Raised if  an exception happened to create such an instance"""
    pass
