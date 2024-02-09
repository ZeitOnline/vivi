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


>>> print(zeit.cms.testing.xmltotext(link.xml))
<link>
  <head/>
  <body/>
</link>

Now that was pretty boring. Add URL and target:

>>> link.target = '_blank'
>>> link.url = 'http://example.org'
>>> link.blog

Does the blog source matching work?

>>> link.url = 'http://gocept.com'
>>> link.blog.name
'Testblog'

>>> print(zeit.cms.testing.xmltotext(link.xml))
<link>
  <head/>
  <body>
    <target>_blank</target>
    <url>http://gocept.com</url>
  </body>
</link>


Syndication
===========

The target URL is added to the channel on syndication.

Create a channel and insert the link:

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()

>>> import zeit.content.cp.feed
>>> feed =  zeit.content.cp.feed.Feed()
>>> link.uniqueId = 'http://xml.zeit.de/link'
>>> feed.insert(0, link)


>>> print(feed.xml_source)
<channel...>
  <title/>
  <container>
    <block xmlns:ns0="http://namespaces.zeit.de/CMS/link"...
      href="http://xml.zeit.de/link"...
      ns0:href="http://gocept.com" ns0:target="_blank">
      ...
      <title/>
      ...
    </block>
  </container>
  <object_limit>50</object_limit>
</channel>

When the target is removed from the link, the attribute is removed from the
channel:

>>> link.target = None
>>> feed.updateMetadata(link)
>>> print(feed.xml_source)
<channel...>
  <title/>
  <container>
    <block xmlns:ns0="http://namespaces.zeit.de/CMS/link"...
      href="http://xml.zeit.de/link"...
      ns0:href="http://gocept.com">
      ...
      <title/>
      ...
    </block>
  </container>
  <object_limit>50</object_limit>
</channel>


Related content
===============

If a link is referenced as related content by another content object, the XML
representation of that object's related content includes the target URL:

>>> import zeit.cms.testcontenttype.testcontenttype
>>> content = zeit.cms.testcontenttype.testcontenttype.ExampleContentType()

>>> import zeit.cms.related.interfaces
>>> related = zeit.cms.related.interfaces.IRelatedContent(content)

>>> related.related = (link,)
>>> import lxml.etree
>>> print(zeit.cms.testing.xmltotext(content.xml))
<...
<references>
  <reference ...xmlns:ns0="http://namespaces.zeit.de/CMS/link"
             type="intern" href="http://xml.zeit.de/link"...
             ns0:href="http://gocept.com">
    ...
  </reference>
</references>
...

rel=nofollow support
--------------------

>>> link.nofollow = True
>>> related.related = (link,)
>>> print(zeit.cms.testing.xmltotext(content.xml))
<...
<references>
  <reference ...xmlns:ns0="http://namespaces.zeit.de/CMS/link"
             type="intern" href="http://xml.zeit.de/link"...
             ns0:href="http://gocept.com" ns0:rel="nofollow">
    ...
  </reference>
</references>
...
