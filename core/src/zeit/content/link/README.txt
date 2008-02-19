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
