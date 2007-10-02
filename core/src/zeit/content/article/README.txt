=======
Article
=======

We need to set the site since we're a functional test:

>>> import zope.app.component.hooks
>>> old_site = zope.app.component.hooks.getSite()
>>> zope.app.component.hooks.setSite(getRootFolder())

Articles consist of an XMLdocument. Most properties map to XML-Elements:
  
>>> import StringIO
>>> from zeit.content.article.article import Article
>>> article_xml = StringIO.StringIO("""\
... <?xml version="1.0" encoding="UTF-8"?>
... <article>
...  <body>
...    <supertitle>Neujahrsansprache</supertitle>
...    <title>Jahr der Überraschungen</title>
...    <subtitle>
...      Kanzlerin Angela Merkel ruft die Deutschen auf, sich auch 2007 wieder
...      selbst zu überra schen. Von einer Reformpause will sie nichts wissen
...    </subtitle>
...  </body>
... </article>
... """)
>>> article = Article(article_xml)
>>> article
<zeit.content.article.article.Article object at 0x...>

The article property is mapped to the XML:

>>> article.title
u'Jahr der \xdcberraschungen'


Changes Are Reflected in The Properties And the XML
===================================================


We change some attributes now and see that the changes are reflected in the
XML:

>>> article.title = u'Jahr ohne \xdcberraschungen'
>>> article.year = 2007
>>> article.volume = 1
>>> article.textLength = 4711
>>> import lxml.etree
>>> print lxml.etree.tostring(article.xml, pretty_print=True)
<article>
  <body>
      <supertitle>Neujahrsansprache</supertitle>
      <title>Jahr ohne &#220;berraschungen</title>
      <subtitle>
      Kanzlerin Angela Merkel ruft die Deutschen auf, sich auch 2007 wieder
      selbst zu &#252;berra schen. Von einer Reformpause will sie nichts
      wissen
      </subtitle>
  </body>
  <head>
    <attribute ns="http://namespaces.zeit.de/QPS/attributes"
      name="year">2007</attribute>
    <attribute ns="http://namespaces.zeit.de/QPS/attributes"
      name="volume">1</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/document"
      name="text-length">4711</attribute>
  </head>
</article>


When we set an attribute multiple times it's just changed:

>>> article.textLength = 1000
>>> article.textLength = 2000
>>> print lxml.etree.tostring(article.xml, pretty_print=True)
<article>
  <body>
      <supertitle>Neujahrsansprache</supertitle>
      <title>Jahr ohne &#220;berraschungen</title>
      <subtitle>
      Kanzlerin Angela Merkel ruft die Deutschen auf, sich auch 2007 wieder
      selbst zu &#252;berra schen. Von einer Reformpause will sie nichts
      wissen
      </subtitle>
  </body>
  <head>
    <attribute ns="http://namespaces.zeit.de/QPS/attributes"
      name="year">2007</attribute>
    <attribute ns="http://namespaces.zeit.de/QPS/attributes"
      name="volume">1</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/document"
      name="text-length">2000</attribute>
  </head>
</article>


`Authors` is a set. We assign a set of authors and expect multiple
`attribute`-tags as result:

>>> article.authors = set(['Bart Simpson', 'Lisa Simpson'])
>>> print lxml.etree.tostring(article.xml, pretty_print=True)
<article>
  <body>
      <supertitle>Neujahrsansprache</supertitle>
      <title>Jahr ohne &#220;berraschungen</title>
      <subtitle>
      Kanzlerin Angela Merkel ruft die Deutschen auf, sich auch 2007 wieder
      selbst zu &#252;berra schen. Von einer Reformpause will sie nichts
      wissen
      </subtitle>
  </body>
  <head>
    <attribute ns="http://namespaces.zeit.de/QPS/attributes"
      name="year">2007</attribute>
    <attribute ns="http://namespaces.zeit.de/QPS/attributes"
      name="volume">1</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/document"
      name="text-length">2000</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/document"
      name="author">Bart Simpson</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/document"
      name="author">Lisa Simpson</attribute>
  </head>
</article>


Article Factory
===============

The article factory parses a Resource's XML and applies the data to the new
article:

>>> from zeit.cms.connector import Resource
>>> from zeit.content.article.article import articleFactory
>>> resource = Resource('/2006/gelsenkirchen', 'gelsenkirchen', 'article',
...                     article_xml)
>>> article = articleFactory(resource)
>>> article
<zeit.content.article.article.Article object at 0x...>
>>> article.title
u'Jahr der \xdcberraschungen'
>>> print article.year
None


Resource Factory
================

The resource factory creates Resource objects from articles:

>>> from zeit.content.article.article import resourceFactory
>>> article = Article(authors=('Tom', 'Jerry'))
>>> resource = resourceFactory(article)
>>> resource.type
'article'
>>> print resource.data.read()
<?xml version='1.0' ...
  ...Tom...Jerry...


Attached Images
===============

Images can be attached to articles. They are stored in the `images` attribute.
Initally there are no images attached to an article:

>>> article = Article()
>>> article.images
()

Get an image from the repository and attach it:

>>> import datetime
>>> import zope.component
>>> import zeit.cms.repository.interfaces
>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)
>>> image = repository['2006']['DSC00109_2.JPG']
>>> image
<zeit.content.image.image.Image object at 0x...>
>>> image.expires = datetime.datetime(2007, 4, 1)
>>> article.images = (image, )

It's now stored on the article:

>>> article.images
(<zeit.content.image.image.Image object at 0x...>,)

And the image is referenced in the XML structure:

>>> print lxml.etree.tostring(article.xml, pretty_print=True)
<article>
  <head>
    ...
    <image
      src="http://xml.zeit.de/2006/DSC00109_2.JPG"
      type="jpeg"
      expires="2007-04-01T00:00:00+00:00">
      <bu></bu>
      <copyright>ZEIT online</copyright>
    </image>...
  </head>
  ...


Cleanup
=======

After tests we clean up:

>>> zope.app.component.hooks.setSite(old_site)
