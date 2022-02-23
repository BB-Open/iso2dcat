from iso2dcat.entities.contactpoint import ContactPoint
from iso2dcat.entities.publisher import Publisher


def to_dcat(node):

    publisher = Publisher(node).run()
    print(publisher)
    contact = ContactPoint(node).run()
    print(contact)

    return publisher