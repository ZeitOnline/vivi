===========
Zeit Search
===========

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
7
>>> item.author
u'pm'

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


Multiple arguments will be anded:

>>> result = metadata(dict(serie='davos', page='39'))
Searching:  (:and (:eq "http://namespaces.zeit.de/CMS/document" "serie" "davos")
                  (:eq "http://namespaces.zeit.de/QPS/attributes" "page" "39"))


Meta search
===========

The meta search aggregates results from various searches. It intersects the
results and combines meta-data from the sources.

>>> meta = zeit.search.search.MetaSearch()

Let's start with two trival cases where no combination is necessary.  When
asking for the index `text` the XapianSearch will be triggered:

>>> result = meta(dict(text='linux'))
>>> len(result)
32
>>> item = sorted(result, key=lambda x: x.uniqueId)[0]
>>> item.title
u'Schwarze M\xe4nner online'
>>> item.uniqueId
u'http://xml.zeit.de/2002/41/200241_public_enemy_xml'


When asking for the other indexes the MetadataSearch will be triggered:

>>> result = meta(dict(serie='davos'))
Searching:  (:eq "http://namespaces.zeit.de/CMS/document" "serie" "davos")
>>> len(result)
3
>>> item = sorted(result, key=lambda x: x.uniqueId)[0]
>>> item.uniqueId
u'http://xml.zeit.de/2006/52/Stimmts'


When we're asking for indexes from two sources at a time the results are
combined:

>>> result = meta(dict(text='linux', serie='davos'))
Searching:  (:eq "http://namespaces.zeit.de/CMS/document" "serie" "davos")
>>> len(result)
1

We had one result only since there is only one common match.

>>> item = sorted(result, key=lambda x: x.uniqueId)[0]
>>> item.uniqueId
u'http://xml.zeit.de/2006/52/Stimmts'

The metadata is merged with the connector taking preference where data was
available:

>>> item.title
u'Kleines Glossar'
>>> item.author
u'pm'
>>> item.year
2006
>>> item.volume
7
>>> item.author
u'pm'
>>> item.page is None
True
