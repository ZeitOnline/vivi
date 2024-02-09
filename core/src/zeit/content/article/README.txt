=======
Article
=======

We need to set the site since we're a functional test:

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()

Articles consist of an XMLdocument. Most properties map to XML-Elements:

>>> from io import StringIO
>>> from zeit.content.article.article import Article
>>> article_xml = StringIO("""\
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
<zeit.content.article.article.Article...>

The article property is mapped to the XML:

>>> article.title
'Jahr der \xdcberraschungen'


Changes Are Reflected in The Properties And the XML
===================================================


We change some attributes now and see that the changes are reflected in the
XML:

>>> article.title = 'Jahr ohne \xdcberraschungen'
>>> article.year = 2007
>>> article.volume = 1
>>> article.textLength = 4711
>>> print(zeit.cms.testing.xmltotext(article.xml))
<article>
  <body>
    <supertitle>Neujahrsansprache</supertitle>
    <title>Jahr ohne Überraschungen</title>
    <subtitle>
     Kanzlerin Angela Merkel ruft die Deutschen auf, sich auch 2007 wieder
     selbst zu überra schen. Von einer Reformpause will sie nichts wissen
   </subtitle>
  </body>
  <head>
    <attribute ns="http://namespaces.zeit.de/CMS/document" name="year">2007</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/document" name="volume">1</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/document" name="text-length">4711</attribute>
  </head>
</article>


When we set an attribute multiple times it's just changed:

>>> article.textLength = 1000
>>> article.textLength = 2000
>>> print(zeit.cms.testing.xmltotext(article.xml))
<article>
  <body>
    <supertitle>Neujahrsansprache</supertitle>
    <title>Jahr ohne Überraschungen</title>
    <subtitle>
     Kanzlerin Angela Merkel ruft die Deutschen auf, sich auch 2007 wieder
     selbst zu überra schen. Von einer Reformpause will sie nichts wissen
   </subtitle>
  </body>
  <head>
    <attribute ns="http://namespaces.zeit.de/CMS/document"
      name="year">2007</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/document"
      name="volume">1</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/document"
      name="text-length">2000</attribute>
  </head>
</article>

`Authors` is a tuple stored in a webdav property. We assign authors we also see
the authors in the xml:

>>> article.authors = ('Bart Simpson', 'Lisa Simpson')
>>> print(zeit.cms.testing.xmltotext(article.xml))
<article>
  <body>
    <supertitle>Neujahrsansprache</supertitle>
    <title>Jahr ohne Überraschungen</title>
    <subtitle>
     Kanzlerin Angela Merkel ruft die Deutschen auf, sich auch 2007 wieder
     selbst zu überra schen. Von einer Reformpause will sie nichts wissen
   </subtitle>
  </body>
  <head>
    <attribute ns="http://namespaces.zeit.de/CMS/document"
      name="year">2007</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/document"
      name="volume">1</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/document"
      name="text-length">2000</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/document"
      name="author">Bart Simpson;Lisa Simpson</attribute>
  </head>
</article>


There is an adapter which sets the text length automatically:

>>> from zeit.content.article.article import updateTextLengthOnChange
>>> updateTextLengthOnChange(article, object())
>>> print(zeit.cms.testing.xmltotext(article.xml))
<article>
  <body>
    <supertitle>Neujahrsansprache</supertitle>
    <title>Jahr ohne Überraschungen</title>
    <subtitle>
     Kanzlerin Angela Merkel ruft die Deutschen auf, sich auch 2007 wieder
     selbst zu überra schen. Von einer Reformpause will sie nichts wissen
   </subtitle>
  </body>
  <head>
    ...
    <attribute ns="http://namespaces.zeit.de/CMS/document"
        name="text-length">194</attribute>
  </head>
</article>


It might happen that the user can change the object (i.e. workflow properties)
but not the textLengh property. Create such an object:

>>> import lxml.etree
>>> import zope.security.interfaces
>>> class NoChangeTextLength:
...
...     xml = lxml.etree.fromstring('<article><body/></article>')
...
...     @property
...     def textLength(self):
...         return None
...
...     @textLength.setter
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

>>> article_xml = StringIO("""\
... <article>
...  <body>
...    <supertitle>Neujahrsansprache</supertitle>
...    <title>Jahr der Überraschungen</title>
...    <subtitle>
...      Kanzlerin Angela Merkel ruft die Deutschen auf, sich auch 2007 wieder
...      selbst zu überra schen. Von einer Reformpause will sie nichts wissen
...    </subtitle>
...  </body>
...  <head>
...    <attribute ns="http://namespaces.zeit.de/CMS/document"
...      name="year">2007</attribute>
...    <attribute ns="http://namespaces.zeit.de/CMS/document"
...      name="volume">2</attribute>
...    <attribute ns="http://namespaces.zeit.de/CMS/document"
...      name="text-length">2000</attribute>
...    <attribute ns="http://namespaces.zeit.de/CMS/document"
...     name="author">Dave Bowman</attribute>
...    <attribute ns="http://namespaces.zeit.de/CMS/document"
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
<zeit.content.article.article.Article...>
>>> article.title
'Jahr der \xdcberraschungen'
>>> print(article.year)
None


Resource Factory
================

The resource factory creates Resource objects from articles:

>>> article = Article()
>>> article.authors = ('Tom', 'Jerry')
>>> resource = ArticleType().resource(article)
>>> resource.type
'article'
>>> print(resource.data.read().decode('utf-8'))
<?xml version='1.0' ...
  ...Tom...Jerry...


Attached Images
===============

Images can be attached to articles. They are stored in the `images` attribute.
Initally there are no images attached to an article:

>>> article = Article()
>>> import zeit.content.image.interfaces
>>> images = zeit.content.image.interfaces.IImages(article)
>>> print(images.image)
None

Get an image from the repository and attach it:

>>> import zeit.cms.testing
>>> _ = zeit.cms.testing.create_interaction('hans')

>>> import datetime
>>> import zope.component
>>> import zeit.cms.repository.interfaces
>>> import zeit.cms.checkout.interfaces
>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)
>>> image = repository['2006']['DSC00109_2.JPG']
>>> image
<zeit.content.image.image.RepositoryImage...>
>>> checked_out = zeit.cms.checkout.interfaces.ICheckoutManager(
...     image).checkout()
>>> image_metadata = zeit.content.image.interfaces.IImageMetadata(checked_out)
>>> image_metadata.expires = datetime.datetime(2007, 4, 1)
>>> checked_in = zeit.cms.checkout.interfaces.ICheckinManager(
...     checked_out).checkin()
>>> images.image = checked_in

It's now stored on the article:

>>> images.image
<zeit.content.image.image.RepositoryImage...>

And the image is referenced in the XML structure:

>>> print(zeit.cms.testing.xmltotext(article.xml))
<article>
  <head>...
    <image...
      src="http://xml.zeit.de/2006/DSC00109_2.JPG"
      type="JPG"...>
      <bu/>
    </image>...
  </head>
  ...


Searchable text
===============

All Text inside <p> elements is extracted (empty paragraphs are ignored):

>>> article_xml = StringIO("""\
... <article>
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
['Link', 'und mehr Text', 'Normaler Absatz']
