import io
from pprint import pprint

from owslib.csw import CatalogueServiceWeb
from lxml import etree
from lxml import objectify
from bs4 import BeautifulSoup as BS

from owslib.fes import PropertyIsLike

from iso2dcat.dcat import to_dcat
from iso2dcat.error import EntityFailed
from iso2dcat.utils import print_error

BATCH_SIZE = 100
TOTAL_COUNT = 10000

# <ogc:Filter>
#
#   <ogc:PropertyIsLike wildCard="%" singleChar="_" escapeChar="/">
#
#    <ogc:PropertyName>apiso:subject</ogc:PropertyName>
#
#    <ogc:Literal>opendata</ogc:Literal>
#
#   </ogc:PropertyIsLike>
#
# </ogc:Filter>

CONSTRAINT = PropertyIsLike(propertyname='apiso:subject', literal='opendata')

def get_records():

    csw = CatalogueServiceWeb('https://geoportal.brandenburg.de/csw-gdi-bb/service')

    batch_start = 0
    while True:
        csw.getrecords2(constraints=[CONSTRAINT], startposition=batch_start, maxrecords=BATCH_SIZE, esn='full',outputschema="http://www.isotc211.org/2005/gmd")
        batch_start += BATCH_SIZE
        if batch_start > TOTAL_COUNT:
            break
        for idx in csw.records:
            rec = csw.records[idx]
            yield rec, idx


histo = {}
good = 0
bad = 0
for rec, idx in get_records():

    try:
        parser = etree.XMLParser(remove_blank_text=True)
        lookup = etree.ElementNamespaceClassLookup(objectify.ObjectifyElementClassLookup())
        parser.setElementClassLookup(lookup)
        with open('xml/rec_{}.xml'.format(idx),'wb') as outfile:
            outfile.write(rec.xml)

        xml_file = io.BytesIO(rec.xml)
#        soup = BS(xml_file, 'xml')
#        node = etree.parse(xml_file, parser=parser).getroot()

        node = etree.parse(xml_file)

        publisher = to_dcat(node)
    except EntityFailed:
        print_error(rec)


    if publisher is None:
        print('Error')
        bad += 1
    else:
        try:
            pub_name = publisher[0].text
            print(pub_name)
            if pub_name in histo:
                histo[pub_name] += 1
            else:
                histo[pub_name] = 1

            good += 1
        except Exception as e:
            print('Error')
            bad += 1

print('good {} bad {}'.format(good, bad))
pprint(histo)