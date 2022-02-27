import tempfile

import prettytable as pt
import zope
from zope import component
from zope.interface.adapter import AdapterRegistry

from iso2dcat.component.interface import IStat


@zope.interface.implementer(IStat)
class Stat:
    """
    Statistical logger
    """

    def __init__(self):
        self.data = {}

    def get_stats(self, cls):
        cls_name = cls.__name__
        if cls_name not in self.data:
            return
        table = pt.PrettyTable()
        table.field_names = [cls_name,"#", "uuids"]

        keys = self.data[cls_name]
        sorted_keys = sorted(keys)
        yield '{}: '.format(cls_name)
        for key in sorted_keys:
            val = self.data[cls_name][key]
            if isinstance(val, int):
                table.add_row([key, val, None])
#                yield '{}:{}'.format(key, val)
            else:
                if len(val) > 0:
                    table.add_row([key, len(val), val[0]])
#                    yield '{}:{}    {}'.format(key, len(val), val[0])
                else:
                    table.add_row([key, len(val), '[]'])
#                    yield '{}:{}    []'.format(key, len(val))
        for line in table.__str__().split('\n'):
            yield line

    def inc(self, inst, stat, no_uuid=False):
        cls_name = inst.__class__.__name__
        if cls_name not in self.data:
            self.data[cls_name] = {}
        if no_uuid :
            increment = 1
        else:
            increment = [inst.uuid]
        if stat not in self.data[cls_name]:
            self.data[cls_name][stat] = increment
        else:
            self.data[cls_name][stat] += increment


def register_stat():
    stat = Stat()
    component.provideUtility(stat, IStat)
    return stat
