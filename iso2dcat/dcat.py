from iso2dcat.entities.contactpoint import ContactPoint
from iso2dcat.entities.publisher import Publisher


def to_dcat(node):

    publisher = Publisher(node).run()
    contact = ContactPoint(node).run()

    return publisher