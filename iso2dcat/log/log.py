# -*- coding: utf-8 -*-
import iso2dcat
from iso2dcat.component.interface import ICfg, IDBFunc
from iso2dcat.component.interface import ILogger
from iso2dcat.exceptions import LogPathNotExists
from iso2dcat.path_utils import dir_not_found_hint
from logging import ERROR
from logging import FileHandler
from logging import Formatter
from logging import getLogger
from logging import StreamHandler
from sys import stdout
from zope import component

import datetime
import os
import zope


# Log level codes according to DB-Definition and syslog
SYSLOG_ERROR = 3
SYSLOG_WARN = 4
SYSLOG_INFO = 6
SYSLOG_DEBUG = 7


@zope.interface.implementer(ILogger)
class Logger:
    """
    Logger class for logging to console, file and DB
    """
    logger = None
    db_log_func = None
    db_log_level = None

    def __init__(self):
        self.setup_logger()

    @property
    def cfg(self):
        return component.queryUtility(ICfg)

    def log_message(self, msg, file_id=None):
        out_msg = '{}{}'.format(file_id or '', msg)
        return out_msg

    def critical(self, msg, file_id=None):
        self.logger.critical(self.log_message(msg, file_id))
        self.db_log(SYSLOG_ERROR, msg, file_id)

    def fatal(self, msg, file_id=None):
        self.logger.fatal(self.log_message(msg, file_id))
        self.db_log(SYSLOG_ERROR, msg, file_id)

    def error(self, msg, file_id=None):
        self.logger.error(self.log_message(msg, file_id))
        self.db_log(SYSLOG_ERROR, msg, file_id)

    def warning(self, msg, file_id=None):
        self.logger.warning(self.log_message(msg, file_id))
        self.db_log(SYSLOG_WARN, msg, file_id)

    def info(self, msg, file_id=None):
        self.logger.info(self.log_message(msg, file_id))
        self.db_log(SYSLOG_INFO, msg, file_id)

    def debug(self, msg, file_id=None):
        self.logger.debug(self.log_message(msg, file_id))
        self.db_log(SYSLOG_DEBUG, msg, file_id)

    def setLevel(self, level):
        # ToDo unclear how to manage levels here
        self.logger.setLevel(level)
        self.db_log_level = level

    def get_logger_formatter(self):
        """
        Check if a colored log is possible. Return get_logger and formatter instance.
        """
        try:
            from colorlog import ColoredFormatter

            import colorlog

            formatter = ColoredFormatter(
                '%(log_color)s%(asctime)s [%(process)d] '
                '%(levelname)-8s %(message)s',
                datefmt=None,
                reset=True,
                log_colors=self.cfg.log_colors,
                secondary_log_colors={},
                style='%',
            )
            get_logger = colorlog.getLogger


        except Exception as e:  # noqa E841
            #   print(e)
            get_logger = getLogger
            formatter = Formatter(
                '%(asctime)s [%(process)d] '
                '%(levelname)-8s %(message)s',
                '%Y-%m-%d %H:%M:%S',
            )
        return get_logger, formatter

    def setup_console_logger(self, formatter):
        """Console logger"""
        console_handler = StreamHandler(stdout)
        console_formatter = formatter
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(self.cfg.log_level_console)
        self.logger.addHandler(console_handler)

    def setup_file_logger(self, formatter):
        """
        File logger
        Has to be setup when the output filename is known
        """
        if not os.path.exists(self.cfg.LOG_PATH):
            self.error(ERROR, """Log file directory "{path}" does not exists""".format(path=self.cfg.LOG_PATH))
            dir_not_found_hint(self.cfg.LOG_PATH)
            raise LogPathNotExists

        log_file_path = os.path.join(
            self.cfg.LOG_PATH,
            '{id}.log'.format(id=self.meas_id),
        )
        file_handler = FileHandler(log_file_path)
        file_handler_formatter = formatter
        file_handler.setFormatter(file_handler_formatter)
        file_handler.setLevel(self.cfg.log_level_file)
        self.logger.addHandler(file_handler)

    def setup_db_logger(self):
        """
        Setup the DB logger. Should be called from the outside after a DB connection is established
        """
        self.db_log_func = component.queryUtility(IDBFunc).db_log

    def setup_logger(self):
        """
        Staggered setup of loggers.
        First the console logger will come up, then the file logger.
        The db logger has to be brought up via an external call after the DB connection is ensured-
        """
        get_logger, formatter = self.get_logger_formatter()
        self.logger = get_logger('iso2dcat')
        self.logger.setLevel(self.cfg.log_level)

        self.setup_console_logger(formatter)

    def db_log(self, level, msg, file_id):
        if self.db_log_func is None:
            return
        now = datetime.datetime.now()
        self.db_log_func(
            level,
            now,
            self.meas_id,
            file_id,
            iso2dcat.__version__,
            msg)


def register_logger():
    # prohibit more than one logger instance
    logger = component.queryUtility(ILogger)
    if logger is not None:
        return logger

    logger = Logger()  # ToDo Ina Where to get the module_version for logging ?
    component.provideUtility(logger, ILogger)
    return logger


def register_db_logger():
    # prohibit more than one logger instance
    logger = component.queryUtility(ILogger)
    logger.setup_db_logger()
