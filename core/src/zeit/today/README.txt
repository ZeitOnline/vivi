=======================
today.xml click counter
=======================

`zeit.today` reads the today.xml click counter and provides an adapter to
`IAccessCounter`.

Set up the product config:

>>> import os
>>> import zope.app.appsetup.product
>>> config = zope.app.appsetup.product._configs['zeit.today'] = {}
>>> config['today-xml-url'] = 'file://%s' % os.path.join(
...     os.path.dirname(__file__), 'today.xml')


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
>>> import pprint

An article has less:
>>> count_util.get_count('http://xml.zeit.de/2007/48/W-Aufmacher-48')
246

When we ask for an object the utility doesn't know about we get None:

>>> count_util.get_count('http://xml.zeit.de/2020/index') is None
True

When we ask for an completly wrong `unique_id` we get None, too:

>>> count_util.get_count('asdf') is None
True
