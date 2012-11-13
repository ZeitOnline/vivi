Teaser groups (feature #6385)
=============================

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()
>>> import zeit.cms.interfaces
>>> from zeit.content.cp.teasergroup.teasergroup import TeaserGroup
>>> teasergroup = TeaserGroup()
>>> teasergroup.teasers
()
>>> teasergroup.teasers = (
...     zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/testcontent'),
...     zeit.cms.interfaces.ICMSContent(
...         'http://xml.zeit.de/online/2007/01/Somalia'),
...     zeit.cms.interfaces.ICMSContent(
...         'http://xml.zeit.de/online/2007/01/eta-zapatero'),
... )
>>> teasergroup.name = u'A nice test group'
>>> teasergroup.automatically_remove
True
>>> teasergroup.automatically_remove = False

Send an created event:

>>> import zope.event
>>> import zope.lifecycleevent
>>> zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(teasergroup))

The teasergroup only stores keyreferences to the actual objects:

>>> teasergroup._teasers
(<zeit.cms.content.keyreference.CMSContentKeyReference object at 0x3e94730>,
 ...


Adding a teaser group to database also assigns a uniqueId:

>>> teasergroup.uniqueId is None
True
>>> teasergroup.create()
>>> print teasergroup.uniqueId
teasergroup://A nice test group
>>> teasergroup.__parent__
<zeit.content.cp.teasergroup.teasergroup.Repository object at 0x4480d30>
>>> teasergroup.__name__
u'A nice test group'
>>> zeit.content.cp.teasergroup.interfaces.IRepository.providedBy(
...     teasergroup.__parent__)
True
>>> zeit.cms.interfaces.ICMSContent.providedBy(teasergroup)
True
>>> zeit.cms.interfaces.ICMSContent(teasergroup.uniqueId) == teasergroup
True

Teasergroups have a last semantic change (which is important for searching):

>>> import zeit.cms.content.interfaces
>>> zeit.cms.content.interfaces.ISemanticChange(
...     teasergroup).last_semantic_change
datetime.datetime(...)


Relateds
========

Relateds contain all but teasers:

>>> import zeit.cms.related.interfaces
>>> related = zeit.cms.related.interfaces.IRelatedContent(teasergroup)
>>> len(related.related)
3
>>> [x.uniqueId for x in related.related]
[u'http://xml.zeit.de/testcontent',
 u'http://xml.zeit.de/online/2007/01/Somalia', 
 u'http://xml.zeit.de/online/2007/01/eta-zapatero']

An empty teasergroup yields no teasers:

>>> empty = TeaserGroup()
>>> zeit.cms.related.interfaces.IRelatedContent(empty).related
()
>>> empty.teasers = ()
>>> zeit.cms.related.interfaces.IRelatedContent(empty).related
()

Images
======

Images "redirect" to the first teaser.

>>> import zeit.content.image.interfaces
>>> images = zeit.content.image.interfaces.IImages(teasergroup)
>>> print images.image
None

>>> import zeit.cms.checkout.helper
>>> content = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/testcontent')
>>> image = zeit.cms.interfaces.ICMSContent(
...     'http://xml.zeit.de/2006/DSC00109_2.JPG')
>>> with zeit.cms.testing.interaction():
...     with zeit.cms.checkout.helper.checked_out(content) as co:
...         zeit.content.image.interfaces.IImages(co).image = image

>>> images = zeit.content.image.interfaces.IImages(teasergroup)
>>> images.image
<zeit.content.image.image.RepositoryImage object at 0x431c410>


Search
======

The fulltext result consists of the title and all teasers:

>>> import zope.index.text.interfaces
>>> searchable_text = zope.index.text.interfaces.ISearchableText(teasergroup)
>>> searchable_text.getSearchableText()
[u'A nice test group']

Define an index:

>>> class TestIndex(object):
...     def __init__(self, context):
...         self.context = context
...     def getSearchableText(self):
...         return [self.context.uniqueId]
>>> import zope.component
>>> gsm = zope.component.getGlobalSiteManager()
>>> gsm.registerAdapter(
...     TestIndex, (zope.interface.Interface,),
...     zope.index.text.interfaces.ISearchableText)
>>> searchable_text.getSearchableText()
[u'A nice test group',
 u'http://xml.zeit.de/testcontent',
 u'http://xml.zeit.de/online/2007/01/Somalia',
 u'http://xml.zeit.de/online/2007/01/eta-zapatero']


>>> gsm.unregisterAdapter(
...     TestIndex, (zope.interface.Interface,),
...     zope.index.text.interfaces.ISearchableText)
True


Auto delete
===========

Teasergroups are automatically deleted after some time if the
``automatically_remove`` flag is set. This is implemented in the repository:

>>> repository = zope.component.getUtility(
...     zeit.content.cp.teasergroup.interfaces.IRepository)
>>> repository.AUTOREMOVE_AFTER
datetime.timedelta(...)

>>> list(repository.keys())
[u'A nice test group']


Lower the time to a second and sweep:

>>> import datetime
>>> import time
>>> repository.AUTOREMOVE_AFTER = datetime.timedelta(seconds=1)
>>> time.sleep(1)
>>> repository.sweep()
>>> list(repository.keys())
[u'A nice test group']

The object was will there as it was not marked for auto remove. Mark it for
removal and sweep again:

>>> teasergroup.automatically_remove = True
>>> repository.sweep()
>>> list(repository.keys())
[]

There is a runner/main method to trigger sweep:

>>> zeit.content.cp.teasergroup.teasergroup.sweep_repository
<function sweep_repository at 0x4265c70>
