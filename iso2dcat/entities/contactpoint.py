# -*- coding: utf-8 -*-

from rdflib import Literal, URIRef

from iso2dcat.entities.base import BaseEntity
from iso2dcat.exceptions import EntityFailed
from iso2dcat.namespace import vcard


class ContactPoint(BaseEntity):
    _stat_title = 'ContactPoints'
    _stat_desc = 'Details show what kind of ISO:Responsible Party is used to create the ContactPoint'
    _stat_uuid = True
    _stat_count = True
    dcat_class = 'vcard_Kind'

    simple_mapping = {
        'gmd:organisationName': 'organization',
        'gmd:deliveryPoint': 'street-address',
        'gmd:city': 'locality',
        'gmd:postalCode': 'postal-code',
        'gmd:administrativeArea': 'region',
        'gmd:country': 'country-name',
        'gmd:electronicMailAddress': 'email',
        'gmd:voice': 'voice',
        'gmd:facsimile': 'fax',
    }
    PUBLISHER_ORG_EXPR = './/gmd:CI_ResponsibleParty[gmd:role/gmd:CI_RoleCode/@codeListValue=$role]'

    # The list of roles defining the order to lookup
    ROLES = ['pointOfContact', 'distributor', 'custodian', 'publisher', 'owner']

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
            self.inc('Processed')
            # get a list of possible publishers
            results = self.node.xpath(self.PUBLISHER_ORG_EXPR, role=role,
                                      namespaces={'gmd': 'http://www.isotc211.org/2005/gmd'})

            if not results:
                continue
            else:
                self.inc(role)
                self.add_entity_type()
                for result in results:
                    # For each simple mapping
                    for selector, target in self.simple_mapping.items():
                        # get a list of possible publishers
                        hits = result.xpath('.//' + selector + '/gco:CharacterString[text()]',
                                            namespaces=self.nsm.namespaces)

                        for hit in hits:
                            if hit:
                                for lang in languages:
                                    self.add_tripel(URIRef(self.uri), vcard[target], Literal(hit, lang=lang))
                break
        if len(self.rdf) == 0:
            self.inc('Bad')
            raise EntityFailed('No ContactPoint')
        else:
            self.inc('Good')
