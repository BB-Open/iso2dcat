from iso2dcat.entities.base import BaseEntity

DATE_QUERY= "gmd:identificationInfo[1]/*/gmd:citation/*/gmd:date/*[gmd:dateType/*/@codeListValue=?role]/gmd:date/*"


class DateMapper(BaseEntity):
    cached_keywords = {}

    def __init__(self, node, parent_uri):
        super().__init__(node)
        self.parent_ressource_uri = parent_uri
        self.roles = ['revision', 'creation', 'publication']

    def run(self):
        # modified
        roles = ['creation', 'revision']
        for role in roles:
            # results = self.node.xpath(DATE_QUERY, role=role,
            #                          namespaces=self.nsm.namespaces)
            # print(results)
            pass

        # issued
        roles = ['revision', 'publication']
