# -*- coding: utf-8 -*-
from rdflib import URIRef, Literal
from rdflib.namespace import FOAF

from iso2dcat.entities.base import BaseEntity
from iso2dcat.exceptions import EntityFailed


class Publisher(BaseEntity):

    dcat_class = 'foaf_Agent'
    entity_type = FOAF.Agent
    roles = ['publisher', 'owner', 'distributor', 'custodian', 'pointOfContact']

    def run(self):
        """
        Retrieve the name organization of the publisher

        In ISO there is no required field for publisher. There is a "publisher" role that can be attributed to certain
        gmd:CI_ResponsibleParty entities. But IMHO a "publisher" role is not required to exist on a dataset.

        So we need a fallback if there is no gmd:CI_ResponsibleParty entity with a role "publisher".

        The straight forward strategy is to look for gmd:CI_ResponsibleParty entities with role "publisher" and then step
        down to roles "owner" and "pointOfContact".

        :return: the organisation of the publisher
        """

        # XPath expression.
        # Find all gmd:CI_ResponsibleParty entities,
        # - which have a role "$role" (given as a parameter)
        # and then get their gmd:organisationName entity
        PUBLISHER_ORG_EXPR = './/gmd:CI_ResponsibleParty[gmd:role/gmd:CI_RoleCode/@codeListValue=$role]//gmd:organisationName/gco:CharacterString[text()]'
#        PUBLISHER_ORG_EXPR = ".//gmd:CI_ResponsibleParty[gmd:role/gmd:CI_RoleCode/@codeListValue=$role]"

        publisher = None
        # For each role
        res = {}
        for role in self.roles:
            # get a list of possible publishers
            publishers = self.node.xpath(PUBLISHER_ORG_EXPR, role=role, namespaces=self.nsm.namespaces)

            # if there is a result
            if len(publishers) > 0:
                # the publisher is the first entry (this can be refined)
                publisher = publishers[0]
                # We have an answer so leave the loop
                self.inc(role)
                self.role = role
                break


        if publisher is None:
            self.inc('bad')
            self.role = None
            raise EntityFailed("No {klass} found".format(klass=self.dcat_class))
        else:
            self.inc('good')

        self.add_entity_type()
        for lang in self.get_languages():
            self.rdf.add((URIRef(self.uri), FOAF.name, Literal(publisher, lang=lang)))

        return self.rdf


class Contributor(Publisher):

    roles = ['contributor']
    dcat_class = 'foaf_Agent_dct_Contributor'


class Maintainer(Publisher):

    roles = ['custodian']
    dcat_class = 'foaf_Agent_dcatde_Maintainer'
