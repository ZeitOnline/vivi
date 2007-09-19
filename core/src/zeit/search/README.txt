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
