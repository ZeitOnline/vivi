===========
Link object
===========


The link object basically stores a URL. For syndication etc. it is possible to
store the common metadata as well.

Instantiate a link and verify the initial xml:

>>> import zeit.content.link.link
>>> link = zeit.content.link.link.Link()

Verify the interfaces:

>>> import zope.interface.verify
>>> import zeit.cms.interfaces
>>> import zeit.content.link.interfaces
>>> zope.interface.verify.verifyObject(
...     zeit.content.link.interfaces.ILink, link)
True
>>> zope.interface.verify.verifyObject(
...     zeit.cms.interfaces.IEditorialContent, link)
True


>>> import lxml.etree
>>> print lxml.etree.tostring(link.xml, pretty_print=True)
<link xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <head/>
  <body/>
</link>

Now that was pretty boring. Add title, URL and target:

>>> link.title = 'gocept'
>>> link.url = 'http://gocept.com'
>>> link.target = '_blank'
>>> print lxml.etree.tostring(link.xml, pretty_print=True)
<link xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <head/>
  <body>
    <title>gocept</title>
    <url>http://gocept.com</url>
    <target>_blank</target>
  </body>
</link>


Syndication
===========

The target URL is added to the channel on syndication.

Create a channel and insert the link[#functional]_:

>>> import zeit.cms.syndication.feed
>>> feed = zeit.cms.syndication.feed.Feed()
>>> link.uniqueId = 'http://xml.zeit.de/link'
>>> feed.insert(0, link)


>>> print feed.xml_source
<channel xmlns:xsd="http://www.w3.org/2001/XMLSchema"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <title/>
  <container>
    <block xmlns:ns0="http://namespaces.zeit.de/CMS/link"
      href="http://xml.zeit.de/link"...
      ns0:href="http://gocept.com" ns0:target="_blank">
      <supertitle xsi:nil="true"/>
      <title xsi:nil="true"/>
      <text xsi:nil="true"/>
      <description xsi:nil="true"/>
      <byline xsi:nil="true"/>...
    </block>
  </container>
  <object_limit>50</object_limit>
</channel>

When the target is removed from the link, the attribute is removed from the
channel:

>>> link.target = None
>>> feed.updateMetadata(link)
>>> print feed.xml_source
<channel xmlns:xsd="http://www.w3.org/2001/XMLSchema"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <title/>
  <container>
    <block xmlns:ns0="http://namespaces.zeit.de/CMS/link"
      href="http://xml.zeit.de/link"...
      ns0:href="http://gocept.com">
      <supertitle xsi:nil="true"/>
      <title xsi:nil="true"/>
      <text xsi:nil="true"/>
      <description xsi:nil="true"/>
      <byline xsi:nil="true"/>
    </block>
  </container>
  <object_limit>50</object_limit>
</channel>


Related content
===============

If a link is referenced as related content by another content object, the XML
representation of that object's related content includes the target URL:

>>> import zeit.cms.testcontenttype.testcontenttype
>>> content = zeit.cms.testcontenttype.testcontenttype.TestContentType()

>>> import zeit.cms.related.interfaces
>>> related = zeit.cms.related.interfaces.IRelatedContent(content)

>>> related.related = (link,)
>>> import lxml.etree
>>> print lxml.etree.tostring(related.xml, pretty_print=True)
<references xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <reference ...xmlns:ns0="http://namespaces.zeit.de/CMS/link"
             type="intern" href="http://xml.zeit.de/link"...
             ns0:href="http://gocept.com">
    ...
  </reference>
</references>


.. [#functional] 

    >>> import zeit.cms.testing
    >>> zeit.cms.testing.set_site()
