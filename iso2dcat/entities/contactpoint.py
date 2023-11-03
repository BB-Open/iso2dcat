# -*- coding: utf-8 -*-
from pkan_config.namespaces import VCARD, NAMESPACES
from rdflib import Literal, RDF

from iso2dcat.entities.base import BaseEntity
from iso2dcat.exceptions import EntityFailed


class ContactPoint(BaseEntity):
    _stat_title = 'ContactPoints (vcard:Kinds)'
    _stat_desc = 'Details show what kind of ISO:Responsible ' \
                 'Party is used to create the ContactPoint'
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

    namespaces = {'vcard': VCARD}
    entity_type = VCARD.Kind

    def run(self):
        """
        Retrieve the vcard information

        :return: vcard
        """
        languages = self.get_languages()
        contact_uris = []
        # For each role
        for role in self.ROLES:
            self.inc('Processed')
            # get a list of possible publishers
            results = self.node.xpath(self.PUBLISHER_ORG_EXPR, role=role,
                                      namespaces=self.nsm.namespaces)

            if not results:
                continue
            else:
                self.inc(role)
                result_objects = []
                for idx, result in enumerate(results):
                    result_triples = {}

                    for selector, target in self.simple_mapping.items():
                        # get a list of possible publishers
                        hits = result.xpath('.//' + selector + '/gco:CharacterString[text()]',
                                            namespaces=self.nsm.namespaces)
                        hit = ''
                        for element in hits:
                            if not hit:
                                hit = str(element)
                            else:
                                hit = hit + ', ' + str(element)
                        if hit:
                            result_triples[VCARD[target]] = hit
                            # for lang in languages:
                            #     self.add_tripel(
                            #         self.make_uri_ref(uri),
                            #         VCARD[target],
                            #         Literal(hit, lang=lang)
                            #     )
                    if result_triples not in result_objects:
                        result_objects.append(result_triples)
                # sorting makes sure _0 is the one with the most information. Could be helpfull for frontend or if just
                #  one result should be added to triple store
                sortedResults = sorted(result_objects, key=lambda x: len(x), reverse=True)
                for idx, result in enumerate(sortedResults):
                    # For each simple mapping
                    uri = self.uri + '_' + str(idx)
                    contact_uris.append(uri)
                    uri_ref = self.make_uri_ref(uri)
                    self.add_tripel(uri_ref, RDF.type, self.entity_type)
                    for field, value in result.items():
                        for lang in languages:
                            self.add_tripel(uri_ref, field, Literal(value, lang=lang))
                break
        if len(self.rdf) == 0:
            self.inc('Bad')
            raise EntityFailed('No ContactPoint')
        else:
            self.inc('Good')
        return contact_uris
