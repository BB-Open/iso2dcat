# -*- coding: utf-8 -*-

from rdflib import Literal, Namespace, URIRef

from iso2dcat.entities.base import BaseEntity



class ContactPoint(BaseEntity):

    dcat_class = 'vcard_Kind'

    simple_mapping = {
        'gmd:deliveryPoint': 'street-address',
        'gmd:city': 'locality',
        'gmd:postalCode': 'postal-code',
        'gmd:administrativeArea': 'region',
        'gmd:country': 'country-name',
        'gmd:electronicMailAddress' : 'email',
    }
    PUBLISHER_ORG_EXPR = './/gmd:CI_ResponsibleParty[gmd:role/gmd:CI_RoleCode/@codeListValue=$role]'

    # The list of roles defining the order to lookup
    ROLES = ['pointOfContact',  'distributor', 'custodian', 'publisher', 'owner']

    vcard = Namespace('http://www.w3.org/2006/vcard/ns#')
    namespaces = {'vcard': vcard}
    entity_type = vcard.Kind

    def run(self):
        """
        Retrieve the vcard information

        :return: vcard
        """
        languages = self.get_languages()
        # For each role
        for role in self.ROLES:
            # get a list of possible publishers
            results = self.node.xpath(self.PUBLISHER_ORG_EXPR, role=role, namespaces={'gmd': 'http://www.isotc211.org/2005/gmd'})

            if not results:
                continue
            else:
                self.inc(role)
                for result in results:
                    # For each simple mapping
                    for selector, target in self.simple_mapping.items():
                        # get a list of possible publishers
                        hits = result.xpath('.//' + selector + '/gco:CharacterString[text()]', namespaces=self.nsm.namespaces)

                        for hit in hits:
                            if hit:
                                for lang in languages:
                                    self.rdf.add((URIRef(self.uri), self.vcard[target], Literal(hit, lang=lang)))
                break
        if len(self.rdf) == 0:
            self.inc('bad')
        else:
            self.inc('good')

        return self.rdf
