# -*- coding: utf-8 -*-
import sys
import traceback

from zope import component

from iso2dcat.component.interface import ILogger


def strip(in_str):
    return in_str.replace('\n', '').replace('\t', '').replace(' ', '')


def print_error(uuid):
    logger = component.queryUtility(ILogger)
    logger.error(str(uuid) + ' failed with EntityFailed')
    ex_type, ex_value, ex_traceback = sys.exc_info()

    # Extract unformatter stack traces as tuples
    trace_back = traceback.extract_tb(ex_traceback)

    # Format stacktrace
    stack_trace = list()

    for trace in trace_back:
        stack_trace.append(
            "File : %s , Line : %d, Func.Name : %s, Message : %s" % (
                trace[0],
                trace[1],
                trace[2],
                trace[3])
        )

    logger.error("Exception type : %s " % ex_type.__name__)
    logger.error("Exception message : %s" % ex_value)
    logger.error("Stack trace : %s" % stack_trace)
