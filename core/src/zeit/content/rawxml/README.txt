Raw XML
=======

The raw xml type is mainly there to support arbitrary blocks in
channels[#functional]_.


Basics
++++++

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


The resource representation's body only contains the raw xml. The title is
stored in a webdav property:

>>> import pprint
>>> resource = zeit.connector.interfaces.IResource(content)
>>> pprint.pprint(dict(resource.properties))
{('title', u'http://namespaces.zeit.de/CMS/document'): u'Roh'}
>>> resource.data.read()
"<?xml version='1.0' encoding='UTF-8'?>\n<a/>\n"
>>> resource.data.seek(0)
>>> resource.type
'rawxml'

Let's add the content to the repository:

>>> repository['raw'] = content


We can of course get the object back:

>>> new_content = repository['raw']
>>> new_content
<zeit.content.rawxml.rawxml.RawXML object at 0x...>

All the data is still there:

>>> new_content.title
u'Roh'
>>> new_content.xml
<Element a at ...>
>>> import lxml.etree
>>> lxml.etree.tostring(new_content.xml)
'<a/>'


Syndication
+++++++++++

One of the interesting features about the raw xml content is that all its
content is added to a channel on syndication. Add the content created above to
a channel:

>>> channel = repository['politik.feed']
>>> channel.insert(0, content)
>>> print lxml.etree.tostring(channel.xml, pretty_print=True)
<channel>
  <title>Politik</title>
  <container>
    <block ...href="http://xml.zeit.de/raw"...>
      <a xmlns:ns0="http://namespaces.zeit.de/CMS/RawXML" ns0:isSyndicatedRawXML="true"/>
    </block>
  </container>
  <object_limit xmlns:py="http://codespeak.net/lxml/objectify/pytype"...>50</object_limit>
</channel>


Let's add some more  xml:

>>> content.xml.append(lxml.objectify.E.foo(bar='baz'))
>>> content.xml.append(lxml.objectify.E.blubs('oink'))
>>> channel.updateMetadata(content)
>>> print lxml.etree.tostring(channel.xml, pretty_print=True)
<channel>
  <title>Politik</title>
  <container>
    <block ...href="http://xml.zeit.de/raw"...>
      <a xmlns:ns0="http://namespaces.zeit.de/CMS/RawXML" ns0:isSyndicatedRawXML="true">
        <foo bar="baz"/>
        <blubs py:pytype="str">oink</blubs>
      </a>
    </block>
  </container>
  <object_limit xmlns:py="http://codespeak.net/lxml/objectify/pytype"...>50</object_limit>
</channel>


Clean up:

>>> zope.app.component.hooks.setSite(old_site)

.. [#functional]

    >>> import zope.app.component.hooks
    >>> old_site = zope.app.component.hooks.getSite()
    >>> zope.app.component.hooks.setSite(getRootFolder())

    >>> import zope.component
    >>> import zeit.cms.repository.interfaces
    >>> repository = zope.component.getUtility(
    ...     zeit.cms.repository.interfaces.IRepository)
