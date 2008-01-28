===========
Zeit Search
===========

Meta search
===========

The meta search aggregates results from various searches. Right now it just
unions the result. The plan is to intersect the results and combine meta-data
from the sources.

Xapian
======

The Xapian search queries an xml interface. For the tests we use a fixed
XML-file as response.

>>> import zeit.search.search
>>> xapian = zeit.search.search.XapianSearch()

The "index" the xapian search handles is `text`:

>>> result = xapian({'text': u'linux'})
>>> len(result)
32
>>> result
set([<zeit.search.search.SearchResult object at 0x...>,
     <zeit.search.search.SearchResult object at 0x...>,
     ...])


>>> item = sorted(result, key=lambda x: x.uniqueId)[0]
>>> item.title
u'Schwarze M\xe4nner online'
>>> item.author
u'Von Thomas Gro\xdf'
>>> item.year
2002
>>> item.volume
41
>>> item.page is None
True
>>> item.uniqueId
u'http://xml.zeit.de/2002/41/200241_public_enemy_xml'
>>> item.__name__
u'200241_public_enemy_xml'


Metadata search
===============

The metadata seach searches the metadata directly via the connector and is the
most up-to-date source.

>>> metadata = zeit.search.search.MetadataSearch()

The metadatasearch handles several "indexes". Try them one at a time:

>>> result = metadata(dict(author='pm'))
Searching:  (:eq "http://namespaces.zeit.de/CMS/document" "author" "pm")

The mock connector always returns the same three elements as result:

>>> len(result)
3
>>> result
set([<zeit.search.search.SearchResult object at 0x...>,
     <zeit.search.search.SearchResult object at 0x...>,
     <zeit.search.search.SearchResult object at 0x...>])
>>> item = sorted(result, key=lambda x: x.uniqueId)[0]

The mock connector doesn't have title metadata:
>>> item.title is None
True
>>> item.volume
'07'
>>> item.author
'pm'

>>> result = metadata(dict(ressort='Deutschland'))
Searching:  (:eq "http://namespaces.zeit.de/CMS/document" "ressort" "Deutschland")

>>> result = metadata(dict(print_ressort='Leben'))
Searching:  (:eq "http://namespaces.zeit.de/QPS/attributes" "ressort" "Leben")

>>> result = metadata(dict(volume='03'))
Searching:  (:eq "http://namespaces.zeit.de/CMS/document" "volume" "03")

>>> result = metadata(dict(year='2007'))
Searching:  (:eq "http://namespaces.zeit.de/CMS/document" "year" "2007")

>>> result = metadata(dict(page='27'))
Searching:  (:eq "http://namespaces.zeit.de/QPS/attributes" "page" "27")

>>> result = metadata(dict(serie='davos'))
Searching:  (:eq "http://namespaces.zeit.de/CMS/document" "serie" "davos")
