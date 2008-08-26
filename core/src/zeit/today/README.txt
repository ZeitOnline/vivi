=======================
today.xml click counter
=======================

`zeit.today` reads the today.xml click counter and provides an adapter to
`IAccessCounter`.

Storage
=======

The `ICountStorage` utility takes care of refreshing and caching today.xml:

>>> import zope.component
>>> import zeit.today.interfaces
>>> count_util = zope.component.getUtility(
...     zeit.today.interfaces.ICountStorage)
>>> count_util
<zeit.today.storage.CountStorage object at 0x...>

Veify the interface:

>>> import zope.interface.verify
>>> zope.interface.verify.verifyObject(
...     zeit.today.interfaces.ICountStorage, count_util)
True

The homepage gets the most hits (for testing we read a local today.xml):

>>> count_util.get_count('http://xml.zeit.de/index')
7992

An article has less:
>>> count_util.get_count('http://xml.zeit.de/2007/48/W-Aufmacher-48')
246

When we ask for an object the utility doesn't know about we get None:

>>> count_util.get_count('http://xml.zeit.de/2020/index') is None
True

When we ask for an completly wrong `unique_id` we get None, too:

>>> count_util.get_count('asdf') is None
True

We can iterate over the entire storage:

>>> sorted(count_util)
['http://xml.zeit.de/1997/26/jurist.txt.19970620.xml',
 'http://xml.zeit.de/1999/10/199910.khmer.neu_.xml', 
 ...]

We can get the date for which the data was returned:

>>> count_util.get_count_date('http://xml.zeit.de/2020/index')


Access counter
==============

There is an adapter from ICMSContent to IAccessCounter. 

>>> import zeit.cms.repository.unknown
>>> content = zeit.cms.repository.unknown.UnknownResource(u'')
>>> content.uniqueId = 'http://xml.zeit.de/index'

Adapt content to IAccessCounter:

>>> import zeit.cms.content.interfaces
>>> counter = zeit.cms.content.interfaces.IAccessCounter(content)
>>> counter
<zeit.today.accesscounter.AccessCounter object at 0x...>
>>> counter.hits
7992

The total hits are none here, because haven't done the functional test setup
and thus the adapter is not found. 

>>> counter.total_hits is None
True


The ``counter`` object implements the IAccessCounter interface:

>>> zope.interface.verify.verifyObject(
...     zeit.cms.content.interfaces.IAccessCounter, counter)
True



Edge cases
==========

There are two edge cases:

1. The today.xml file is empty -- this happens quite regularly throughout the
   day.
2. The today.xml file does not contain any <article> nodes. This happens after
   midnight when the counters have been reset but nothin has been counted so
   far.


Create an empty file and initialize a counter:

>>> import tempfile
>>> fd, name = tempfile.mkstemp()
>>> def url_get():
...     return 'file://' + name
>>> counter = zeit.today.storage.CountStorage(url_get)

Getting objects doesn't raise an exception:

>>> counter.get_count('foo') is None
True

Let's add the root node to verify the second edge case:

>>> open(name, 'w').write("<?xml version='1.0'?>\n<articles/>")
>>> counter = zeit.today.storage.CountStorage(url_get)
>>> counter.get_count('foo') is None
True


Clean up:

>>> import os
>>> os.remove(name)
