Raw XML
=======

The raw xml type is mainly there to support arbitrary blocks in channels.

Create an intance and set some data:

>>> import lxml.objectify
>>> import zeit.content.rawxml.rawxml
>>> content = zeit.content.rawxml.rawxml.RawXML()
>>> content.title = u'Roh'
>>> content.xml = lxml.objectify.fromstring('<a/>')

``content`` provides the IRawXML interface:

>>> import zope.interface.verify
>>> import zeit.content.rawxml.interfaces
>>> zope.interface.verify.verifyObject(
...     zeit.content.rawxml.interfaces.IRawXML, content)
True


add to repository

test adaption to resource

retrieve from repository

