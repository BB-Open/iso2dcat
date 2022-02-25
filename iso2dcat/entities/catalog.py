# -*- coding: utf-8 -*-
from iso2dcat.entities.base import BaseEntity


class Catalog(BaseEntity):

    catalog = {}



    def run(self):
        identifier = self.node.fileIdentifier.getchildren()[0].text
        if identifier in self.dcm.dcm:
            key = self.dcm.dcm[identifier]['publisher']
            if key not in Catalog.catalog:
                Catalog.catalog[key] = 0
            Catalog.catalog[key] += 1

            Catalog.good += 1
        else:
            Catalog.bad += 1

    @classmethod
    def show_stats(cls):
        print('{}: good:{} bad:{}'.format(cls.__name__, cls.good, cls.bad))
        print('pointers\n')

        for key, value in Catalog.catalog.items():
            print('{}:{}'.format(key, value))
