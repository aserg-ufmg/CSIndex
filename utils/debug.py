import xmltodict
import urllib2
import re
import collections

FIRST_YEAR= 2019
LAST_YEAR= 2019

def handle_article(_, article):

    if 'journal' in article:
        print article['title']

    return True


print '###########################################################'

url= "http://dblp.org/pid/" + "t/AgmaJMTraina" + ".xml"


bibfile = urllib2.urlopen(url).read()
bibdata = xmltodict.parse(bibfile, item_depth=3, item_callback=handle_article)
