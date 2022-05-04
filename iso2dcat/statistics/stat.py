import prettytable as pt
import zope
from zope import component
from zope.interface.adapter import AdapterRegistry

from iso2dcat.component.interface import IStat

TOP_STAT_KEYS = ['Processed', 'Good', 'Bad']


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

        meta = self.data[cls_name]
        yield meta['title']
        yield meta['desc']

        stat = meta['stat']

        table = pt.PrettyTable()

        cols = [cls_name]

        if meta['features']['count']:
            cols.append('#')
            table.align['#'] = 'r'

        if meta['features']['uuid']:
            cols.append('Sample UUID')

        table.field_names = cols
        table.align[cls_name] = 'l'

        stat_keys = stat.keys()

        top_keys = []
        normal_keys = []
        for key in TOP_STAT_KEYS:
            if key in stat_keys:
                top_keys.append(key)

        for key in stat_keys:
            if key not in TOP_STAT_KEYS:
                normal_keys.append(key)

        normal_keys.sort()

        def data_rows(keys):
            for key in keys:
                rec = stat[key]
                row = [key]
                if meta['features']['count']:
                    row.append(rec['counts'])
                    if meta['features']['uuid']:
                        if len(rec['uuids']) > 0:
                            row.append(rec['uuids'][0])
                        else:
                            row.append('None')

                table.add_row(row)

        data_rows(top_keys)
        row = ['Details:']
        if meta['features']['count']:
            row.append('')
            if meta['features']['uuid']:
                row.append('')

        table.add_row(row)

        data_rows(normal_keys)

        for line in table.__str__().split('\n'):
            yield line
        yield '\n'

    def inc(self, inst, stat, cls_name=None, increment=1, no_uuid=False):
        entity_rec = self.get_entity_record(inst, cls_name=cls_name)
        rec = self.get_stat_record(stat, entity_rec)
        # try:
        rec['counts'] += increment
        # except :
        #     ra
        if entity_rec['features']['uuid'] and not no_uuid:
            rec['uuids'].append(inst.uuid)

    def init(self, inst, cls_name=None):
        rec = self.get_entity_record(inst, cls_name=cls_name)

    def get_entity_record(self, inst, cls_name=None):
        if not cls_name:
            cls_name = inst.__class__.__name__
        else:
            pass
        if cls_name not in self.data:
            features = {
                'uuid': inst._stat_uuid,
                'count': inst._stat_count,
            }
            stat = {
                'Processed': {
                    'counts': 0,
                    'uuids': [],
                },
                'Good': {
                    'counts': 0,
                    'uuids': [],
                },
                'Bad': {
                    'counts': 0,
                    'uuids': [],
                },
            }
            entity_rec = {
                'stat': stat,
                'title': inst._stat_title,
                'desc': inst._stat_desc,
                'features': features
            }
            self.data[cls_name] = entity_rec
        else:
            entity_rec = self.data[cls_name]
        return entity_rec

    def get_stat_record(self, stat, entity_rec):
        if stat not in entity_rec['stat']:
            stat_rec = {
                'counts': 0,
                'uuids': []
            }
            entity_rec['stat'][stat] = stat_rec
        else:
            stat_rec = entity_rec['stat'][stat]
        return stat_rec


def register_stat():
    stat = component.queryUtility(IStat)
    if stat:
        return stat
    stat = Stat()
    component.provideUtility(stat, IStat)
    return stat
