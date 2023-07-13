Raw XML
=======

The raw xml type is mainly there to support arbitrary blocks in
channels.

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()
>>> import zope.component
>>> import zeit.cms.repository.interfaces
>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)


Basics
++++++

Create an intance and set some data:

>>> import lxml.objectify
>>> import zeit.content.rawxml.rawxml
>>> content = zeit.content.rawxml.rawxml.RawXML()
>>> content.title = 'Roh'
>>> content.xml = lxml.objectify.fromstring('<a/>')

``content`` provides the IRawXML interface:

>>> import zope.interface.verify
>>> import zeit.content.rawxml.interfaces
>>> zope.interface.verify.verifyObject(
...     zeit.content.rawxml.interfaces.IRawXML, content)
True


The resource representation's body only contains the raw xml. The title is
stored in a webdav property:

>>> import pprint
>>> resource = zeit.connector.interfaces.IResource(content)
>>> dict(resource.properties)[
...     ('title', 'http://namespaces.zeit.de/CMS/document')]
'Roh'
>>> resource.data.read()
b"<?xml version='1.0' encoding='UTF-8'?>\n<a/>\n"
>>> _ = resource.data.seek(0)
>>> resource.type
'rawxml'

Let's add the content to the repository:

>>> repository['raw'] = content


We can of course get the object back:

>>> new_content = repository['raw']
>>> new_content
<zeit.content.rawxml.rawxml.RawXML...>

All the data is still there:

>>> new_content.title
'Roh'
>>> new_content.xml
<Element a at ...>
>>> lxml.etree.cleanup_namespaces(new_content.xml)
>>> zeit.cms.testing.xmltotext(new_content.xml)
'<a/>\n'
