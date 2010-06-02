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
... <article xmlns:py="http://codespeak.net/lxml/objectify/pytype">
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
<article xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <body>
    <supertitle>Neujahrsansprache</supertitle>
    <title>Jahr ohne &#220;berraschungen</title>
    <subtitle>
     Kanzlerin Angela Merkel ruft die Deutschen auf, sich auch 2007 wieder
     selbst zu &#252;berra schen. Von einer Reformpause will sie nichts wissen
   </subtitle>
  </body>
  <head>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="year">2007</attribute>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="volume">1</attribute>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="text-length">4711</attribute>
  </head>
</article>


When we set an attribute multiple times it's just changed:

>>> article.textLength = 1000
>>> article.textLength = 2000
>>> print lxml.etree.tostring(article.xml, pretty_print=True)
<article xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <body>
    <supertitle>Neujahrsansprache</supertitle>
    <title>Jahr ohne &#220;berraschungen</title>
    <subtitle>
     Kanzlerin Angela Merkel ruft die Deutschen auf, sich auch 2007 wieder
     selbst zu &#252;berra schen. Von einer Reformpause will sie nichts wissen
   </subtitle>
  </body>
  <head>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document"
      name="year">2007</attribute>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document"
      name="volume">1</attribute>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document"
      name="text-length">2000</attribute>
  </head>
</article>

`Authors` is a tuple stored in a webdav property. We assign authors we also see
the authors in the xml:

>>> article.authors = ('Bart Simpson', 'Lisa Simpson')
>>> print lxml.etree.tostring(article.xml, pretty_print=True)
<article xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <body>
    <supertitle>Neujahrsansprache</supertitle>
    <title>Jahr ohne &#220;berraschungen</title>
    <subtitle>
     Kanzlerin Angela Merkel ruft die Deutschen auf, sich auch 2007 wieder
     selbst zu &#252;berra schen. Von einer Reformpause will sie nichts wissen
   </subtitle>
  </body>
  <head>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document"
      name="year">2007</attribute>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document"
      name="volume">1</attribute>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document"
      name="text-length">2000</attribute>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document"
      name="author">Bart Simpson;Lisa Simpson</attribute>
  </head>
</article>


There is an adapter which sets the text length automatically:

>>> from zeit.content.article.article import updateTextLengthOnChange
>>> updateTextLengthOnChange(article, object())
>>> print lxml.etree.tostring(article.xml, pretty_print=True)
<article xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <body>
    <supertitle>Neujahrsansprache</supertitle>
    <title>Jahr ohne &#220;berraschungen</title>
    <subtitle>
     Kanzlerin Angela Merkel ruft die Deutschen auf, sich auch 2007 wieder
     selbst zu &#252;berra schen. Von einer Reformpause will sie nichts wissen
   </subtitle>
  </body>
  <head>
    ...
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document"
        name="text-length">194</attribute>
  </head>
</article>


It might happen that the user can change the object (i.e. workflow properties)
but not the textLengh property. Create such an object:

>>> import rwproperty
>>> import lxml.objectify
>>> import zope.security.interfaces
>>> class NoChangeTextLength(object):
...
...     xml = lxml.objectify.fromstring('<article><body/></article>')
...
...     @rwproperty.setproperty
...     def textLength(self, value):
...         raise zope.security.interfaces.Unauthorized("textLength")
...
>>> updateTextLengthOnChange(NoChangeTextLength(), object())


Reading the properties from the XML
===================================

Sometimes it is useful to actually instantiate the WebDAV from the
information contained in the XML, for instance when importing from the
Content-Drehscheibe. There is a method on ``Article`` that helps you do
this.

We first define some XML which contains some properties we want to be
reflected in the WebDAV properties:

>>> article_xml = StringIO.StringIO("""\
... <?xml version="1.0" encoding="UTF-8"?>
... <article xmlns:py="http://codespeak.net/lxml/objectify/pytype">
...  <body>
...    <supertitle>Neujahrsansprache</supertitle>
...    <title>Jahr der Überraschungen</title>
...    <subtitle>
...      Kanzlerin Angela Merkel ruft die Deutschen auf, sich auch 2007 wieder
...      selbst zu überra schen. Von einer Reformpause will sie nichts wissen
...    </subtitle>
...  </body>
...  <head>
...    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document"
...      name="year">2007</attribute>
...    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document"
...      name="volume">2</attribute>
...    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document"
...      name="text-length">2000</attribute>
...    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document"
...     name="author">Dave Bowman</attribute>
...    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document"
...     name="empty"></attribute>
...  </head>
... </article>
... """)

We then create an article from it:

>>> article = Article(article_xml)

At this point, the article won't have DAV properties yet:

>>> import zeit.connector.interfaces
>>> properties = zeit.connector.interfaces.IWebDAVProperties(article)
>>> list(properties.keys())
[]
>>> properties.get(('author', 'http://namespaces.zeit.de/CMS/document')) is None
True

We can import the data from the article:

>>> article.updateDAVFromXML()

Now the WebDAV properties are there, besides the empty one:

>>> sorted(properties.keys())
[('author', 'http://namespaces.zeit.de/CMS/document'),
 ('text-length', 'http://namespaces.zeit.de/CMS/document'),
 ('volume', 'http://namespaces.zeit.de/CMS/document'),
 ('year', 'http://namespaces.zeit.de/CMS/document')]
>>> properties.get(('author', 'http://namespaces.zeit.de/CMS/document'))
'Dave Bowman'

Article Factory
===============

The article factory parses a Resource's XML and applies the data to the new
article:

>>> from zeit.cms.connector import Resource
>>> from zeit.content.article.article import ArticleType
>>> resource = Resource('/2006/gelsenkirchen', 'gelsenkirchen', 'article',
...                     article_xml)
>>> article = ArticleType().content(resource)
>>> article
<zeit.content.article.article.Article object at 0x...>
>>> article.title
u'Jahr der \xdcberraschungen'
>>> print article.year
None


Resource Factory
================

The resource factory creates Resource objects from articles:

>>> article = Article()
>>> article.authors = ('Tom', 'Jerry')
>>> resource = ArticleType().resource(article)
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
>>> import zeit.content.image.interfaces
>>> images = zeit.content.image.interfaces.IImages(article)
>>> images.images
()

Get an image from the repository and attach it[#needsinteraction]_:

>>> import datetime
>>> import zope.component
>>> import zeit.cms.repository.interfaces
>>> import zeit.cms.checkout.interfaces
>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)
>>> image = repository['2006']['DSC00109_2.JPG']
>>> image
<zeit.content.image.image.RepositoryImage object at 0x...>
>>> checked_out = zeit.cms.checkout.interfaces.ICheckoutManager(
...     image).checkout()
>>> image_metadata = zeit.content.image.interfaces.IImageMetadata(checked_out)
>>> image_metadata.expires = datetime.datetime(2007, 4, 1)
>>> checked_in = zeit.cms.checkout.interfaces.ICheckinManager(
...     checked_out).checkin()
>>> images.images = (checked_in, )

It's now stored on the article:

>>> images.images
(<zeit.content.image.image.RepositoryImage object at 0x...>,)

And the image is referenced in the XML structure:

>>> print lxml.etree.tostring(article.xml, pretty_print=True)
<article xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <head>...
    <image ...
      src="http://xml.zeit.de/2006/DSC00109_2.JPG"
      type="JPG"...>
      <bu xsi:nil="true"/>
      <copyright...
    </image>...
  </head>
  ...


Comment aggregation
===================

An article (actually all objects with IAssetView) can relate another object for
combining the comments:

>>> comments = zeit.content.article.interfaces.IAggregatedComments(article)
>>> comments
<zeit.content.article.comment.AggregatedComments object at 0x...>
>>> comments.comment_id = repository.getContent(
...     'http://xml.zeit.de/online/2007/01/Somalia')


This is stored in a webdav property:

>>> properties = zeit.connector.interfaces.IWebDAVProperties(article)
>>> properties[('comment-id', 'http://namespaces.zeit.de/CMS/document')]
u'http://xml.zeit.de/online/2007/01/Somalia'
>>> comments.comment_id
<zeit.content.article.article.Article object at 0x...>
>>> comments.comment_id.title
u'R\xfcckkehr der Warlords'


Searchable text
===============

All Text inside <p> elements is extracted (empty paragraphs are ignored):

>>> article_xml = StringIO.StringIO("""\
... <?xml version="1.0" encoding="UTF-8"?>
... <article xmlns:py="http://codespeak.net/lxml/objectify/pytype">
...  <body>
...    <supertitle>Neujahrsansprache</supertitle>
...    <title>Jahr der Überraschungen</title>
...    <p><a href="http://foo">Link</a> und mehr Text</p>
...    <p></p>
...    <p>Normaler Absatz</p>
...  </body>
... </article>
... """)
>>> article = Article(article_xml)
>>> adapter = zope.index.text.interfaces.ISearchableText(article)
>>> adapter.getSearchableText()
[u'Link', u'und mehr Text', u'Normaler Absatz']


Cleanup
=======

After tests we clean up:

>>> zope.security.management.endInteraction()
>>> zope.app.component.hooks.setSite(old_site)


.. [#needsinteraction]

    >>> import zope.publisher.browser
    >>> request = zope.publisher.browser.TestRequest()
    >>> import zope.security.testing
    >>> principal = zope.security.testing.Principal(u'hans')
    >>> request.setPrincipal(principal)
    >>> import zope.security.management
    >>> zope.security.management.newInteraction(request)
