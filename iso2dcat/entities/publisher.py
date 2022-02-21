from iso2dcat.entities.base import Base
from iso2dcat.error import EntityFailed


class Publisher(Base):

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
        PUBLISHER_ORG_EXPR = ".//gmd:CI_ResponsibleParty[gmd:role/gmd:CI_RoleCode/@codeListValue=$role]//gmd:organisationName"
#        PUBLISHER_ORG_EXPR = ".//gmd:CI_ResponsibleParty[gmd:role/gmd:CI_RoleCode/@codeListValue=$role]"

        # The list of roles defining the order to lookup
        roles = ['publisher', 'owner', 'pointOfContact']


        publisher = None
        # For each role
        for role in roles:
            # get a list of possible publishers
            publishers = self.node.xpath(PUBLISHER_ORG_EXPR, role=role, namespaces={'gmd':"http://www.isotc211.org/2005/gmd"})

            # if there is a result
            if len(publishers) > 0:
                # the publisher is the first entry (this can be refined)
                publisher = publishers[0]
                # We have an answer so leave the loop
                break

        if publisher == None:
            raise EntityFailed

        return publisher
