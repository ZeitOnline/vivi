=======
Authors
=======

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()
>>> principal = zeit.cms.testing.create_interaction()

>>> import zeit.cms.repository.interfaces
>>> import zeit.content.author.author
>>> import zeit.content.image.interfaces
>>> import zope.component

>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)
>>> shakespeare = zeit.content.author.author.Author()
>>> shakespeare.title = 'Sir'
>>> shakespeare.firstname = 'William'
>>> shakespeare.lastname = 'Shakespeare'
>>> shakespeare.vgwortid = 12345
>>> repository['shakespeare'] = shakespeare
>>> shakespeare = repository['shakespeare']
>>> print(zeit.cms.testing.xmltotext(shakespeare.xml))
<author...>
  <title>Sir</title>
  <firstname>William</firstname>
  <lastname>Shakespeare</lastname>
  <vgwortid>12345</vgwortid>
  <display_name>William Shakespeare</display_name>
</author>

The default display name is 'Firstname Lastname', but any user-entered value
takes precedence:

>>> shakespeare.entered_display_name = 'Flub'
>>> repository['shakespeare'] = shakespeare
>>> shakespeare = repository['shakespeare']
>>> print(zeit.cms.testing.xmltotext(shakespeare.xml))
<author...>
  <title>Sir</title>
  <firstname>William</firstname>
  <lastname>Shakespeare</lastname>
  <vgwortid>12345</vgwortid>
  <display_name>Flub</display_name>
  <entered_display_name>Flub</entered_display_name>
</author>

>>> shakespeare.entered_display_name = None
>>> repository['shakespeare'] = shakespeare
>>> shakespeare = repository['shakespeare']
>>> print(zeit.cms.testing.xmltotext(shakespeare.xml))
<author...>
  <title>Sir</title>
  <firstname>William</firstname>
  <lastname>Shakespeare</lastname>
  <vgwortid>12345</vgwortid>
  <display_name>William Shakespeare</display_name>
</author>

The author image group is stored using the IImages interface.

>>> images = zeit.content.image.interfaces.IImages(shakespeare)
>>> images.image = repository['2007']['03']['group']
>>> repository['shakespeare'] = shakespeare
>>> shakespeare = repository['shakespeare']
>>> print(zeit.cms.testing.xmltotext(shakespeare.xml))
<author...>
  ...
  <image_group base-id="http://xml.zeit.de/2007/03/group/" type="jpg"/>
</author>

Using authors
=============

The field authorships on ICommonMetadata is used to store authors.
It takes precedence over the freetext authors:

>>> import zope.lifecycleevent
>>> from zeit.cms.content.interfaces import ICommonMetadata
>>> with zeit.cms.checkout.helper.checked_out(repository['testcontent']) as co:
...     co.authorships = [co.authorships.create(shakespeare)]
...     co.authors = ['Charles Dickens']
...     zope.lifecycleevent.modified(co, zope.lifecycleevent.Attributes(
...         ICommonMetadata, 'authorships', 'authors'))
>>> print(zeit.cms.testing.xmltotext(repository['testcontent'].xml))
<testtype>
  <head>
    <author href="http://xml.zeit.de/shakespeare" hdok=""/>
  </head>
  <body/>
</testtype>

>>> with zeit.cms.checkout.helper.checked_out(repository['testcontent']) as co:
...     co.authorships = []
...     co.authors = ['Charles Dickens']
>>> content = repository['testcontent']
>>> print(content.authors)
('Charles Dickens',)

Changes to author objects are propagated to content on checkin:

>>> with zeit.cms.checkout.helper.checked_out(repository['testcontent']) as co:
...     co.authorships = [co.authorships.create(repository['shakespeare'])]
>>> with zeit.cms.checkout.helper.checked_out(repository['shakespeare']) as co:
...     co.lastname = 'Otherwise'
>>> with zeit.cms.checkout.helper.checked_out(repository['testcontent']):
...     pass


Publishing
==========

Authors are published along with the articles that reference them:

>>> with zeit.cms.checkout.helper.checked_out(repository['testcontent']) as co:
...     co.authorships = [co.authorships.create(repository['shakespeare'])]

>>> import zeit.cms.workflow.interfaces
>>> zeit.cms.workflow.interfaces.IPublicationDependencies(
...     repository['testcontent']).get_dependencies()
[<zeit.content.author.author.Author http://xml.zeit.de/shakespeare>]

But not if they are already published (there are no changes that could be
relevant for the article):

>>> info = zeit.cms.workflow.interfaces.IPublishInfo(repository['shakespeare'])
>>> info.published = True
>>> zeit.cms.workflow.interfaces.IPublicationDependencies(
...     repository['testcontent']).get_dependencies()
[]


References
==========

We can track which articles an author is referenced by:

>>> import zeit.cms.relation.interfaces
>>> rel = zope.component.getUtility(
...     zeit.cms.relation.interfaces.IRelations)
>>> [x.uniqueId for x in rel.get_relations(repository['shakespeare'])]
['http://xml.zeit.de/testcontent']


Equality
========

Author objects in the CMS live at
/autoren/<letter>/<Firstname_Lastname>/index.xml,
so the default comparison using __name__ does not do the right thing.
Thus, authors use their uniqueId to check for equality.

>>> repository['andersen'] = zeit.cms.repository.folder.Folder()
>>> repository['byron'] = zeit.cms.repository.folder.Folder()

>>> andersen = zeit.content.author.author.Author()
>>> andersen.firstname = 'Hans Christian'
>>> andersen.lastname = 'Andersen'
>>> repository['andersen']['index.xml'] = andersen

>>> byron = zeit.content.author.author.Author()
>>> byron.firstname = 'George Gordon'
>>> byron.lastname = 'Byron'
>>> repository['byron']['index.xml'] = byron


>>> repository['andersen']['index.xml'] == repository['byron']['index.xml']
False
