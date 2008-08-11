===========
Link object
===========


The link object basically stores an URL. For syndication etc. it is possible to
store the common metadata as well.

Instanciate a link and verify the inital xml:

>>> import zeit.content.link.link
>>> link = zeit.content.link.link.Link()

>>> import lxml.etree
>>> print lxml.etree.tostring(link.xml, pretty_print=True)
<link xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <head/>
  <body/>
</link>

Now that was pretty boring. Add a title and an url:

>>> link.title = 'gocept'
>>> link.url = 'http://gocept.com'
>>> print lxml.etree.tostring(link.xml, pretty_print=True)
<link xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <head/>
  <body>
    <title>gocept</title>
    <url py:pytype="str">http://gocept.com</url>
  </body>
</link>


Syndcation
==========

The target URL is added to the channel on syndication.

Create a channel and insert the link[#functional]_:

>>> import zeit.cms.syndication.feed
>>> feed = zeit.cms.syndication.feed.Feed()
>>> link.uniqueId = 'http://xml.zeit.de/link'
>>> feed.insert(0, link)


>>> print feed.xml_source
<channel xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <title/>
  <container>
    <block xmlns:ns0="http://namespaces.zeit.de/CMS/link"
      href="http://xml.zeit.de/link" ns0:href="http://gocept.com">
      <supertitle xsi:nil="true"/>
      <title xsi:nil="true"/>
      <text xsi:nil="true"/>
      <description xsi:nil="true"/>
      <byline xsi:nil="true"/>
      <short>
        <title xsi:nil="true"/>
        <text xsi:nil="true"/>
      </short>
      <homepage>
        <title xsi:nil="true"/>
        <text xsi:nil="true"/>
      </homepage>
      <references/>
    </block>
  </container>
  <object_limit py:pytype="int">50</object_limit>
</channel>


>>> zope.app.component.hooks.setSite(old_site)

.. [#functional] 

    >>> import zope.app.component.hooks
    >>> old_site = zope.app.component.hooks.getSite()
    >>> zope.app.component.hooks.setSite(getRootFolder())

