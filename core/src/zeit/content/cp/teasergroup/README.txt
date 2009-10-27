Teaser groups (feature #6385)
=============================

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()
>>> import zeit.cms.interfaces
>>> from zeit.content.cp.teasergroup.teasergroup import TeaserGroup
>>> teasergroup = TeaserGroup()
>>> teasergroup.teasers is None
True
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



Relateds
========

Relateds contain all but the first teaser:

>>> import zeit.cms.related.interfaces
>>> related = zeit.cms.related.interfaces.IRelatedContent(teasergroup)
>>> len(related.related)
2
>>> [x.uniqueId for x in related.related]
[u'http://xml.zeit.de/online/2007/01/Somalia', 
 u'http://xml.zeit.de/online/2007/01/eta-zapatero']

An empty teasergroup yields no teasers:

>>> empty = TeaserGroup()
>>> zeit.cms.related.interfaces.IRelatedContent(empty).related
()
>>> empty.teasers = ()
>>> zeit.cms.related.interfaces.IRelatedContent(empty).related
()

A teser group with exactly one teaser also yields no relateds:

>>> one_group = TeaserGroup()
>>> one_group.teasers = (
...     zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/testcontent'),)
>>> zeit.cms.related.interfaces.IRelatedContent(one_group).related
()
