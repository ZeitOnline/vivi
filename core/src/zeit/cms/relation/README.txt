Relations
=========

The relation support is there to answer the question by which objects an object
is referenced by, i.e. to resolve back references. The backreferences are
extrinsic, the referenced object doesn't know about them. The actual
references are usually intrinsic, i.e. the referencing object knows it
references the other object.

Setup
+++++

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()
>>> principal = zeit.cms.testing.create_interaction()
>>> import zope.component
>>> import zeit.cms.repository.interfaces
>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)


Low level support
+++++++++++++++++

The `IRelations`-Utility handles all the magic of resolving
references:

>>> import zeit.cms.relation.interfaces
>>> relations = zope.component.getUtility(
...     zeit.cms.relation.interfaces.IRelations)
>>> relations
<zeit.cms.relation.relation.Relations object at 0x...>

Verify the interface:

>>> import zope.interface.verify
>>> zope.interface.verify.verifyObject(
...     zeit.cms.relation.interfaces.IRelations, relations)
True


Create some testcontent:

>>> from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
>>> repository['a'] = ExampleContentType()
>>> repository['b'] = ExampleContentType()
>>> repository['c'] = ExampleContentType()
>>> repository['d'] = ExampleContentType()
>>> repository['e'] = ExampleContentType()
>>> a = repository['a']

The content doesn't have any relateds currently, nor is it related anywhere:

>>> sorted(relations.get_relations(a))
[]

Relate b and c to a via IRelatedContent

>>> from zeit.cms.checkout.helper import checked_out
>>> import zeit.cms.related.interfaces
>>> with checked_out(repository['a']) as co:
...     related = zeit.cms.related.interfaces.IRelatedContent(co)
...     related.related = (repository['b'], repository['c'])

We could ask for b's relations:

>>> res = sorted(relations.get_relations(repository['b']))
>>> len(res)
1
>>> res
[<zeit.cms.testcontenttype.testcontenttype.ExampleContentType...>]
>>> res[0].uniqueId
'http://xml.zeit.de/a'

The same accounts for c:

>>> res = sorted(relations.get_relations(repository['c']))
>>> res[0].uniqueId
'http://xml.zeit.de/a'


Note that `get_relations` is not transitive. So if d references a, asking for
c's references will still just yield a:

>>> d = repository['d']
>>> related = zeit.cms.related.interfaces.IRelatedContent(d)
>>> related.related = (repository['a'],)
>>> repository['d'] = d

>>> res = sorted(relations.get_relations(repository['c']))
>>> len(res)
1
>>> res[0].uniqueId
'http://xml.zeit.de/a'

When an object with a unique id of "None" is queried, nothing will be returned:

>>> no_uid = ExampleContentType()
>>> sorted(relations.get_relations(no_uid))
[]

When we remove a from the repository, but do not update the index, c will no
longer reference a anyway (because we cannot find a anymore)

>>> del repository['a']
>>> sorted(relations.get_relations(repository['c']))
[]


Event handlers
++++++++++++++

The event handlers listen on various events from `zeit.cms` and keep the
relations uptodate.

Checkin
-------

Clean up previous test state:
>>> for name in ('a', 'b', 'c', 'd'):
...     relations._catalog.unindex_doc(
...         'http://xml.zeit.de/%s' % name)

Objects are indexed before checkin. We will check a out and back in and verify
it is indexed. Let a relate checkout and relate c:

>>> import zeit.cms.checkout.interfaces
>>> checked_out = zeit.cms.checkout.interfaces.ICheckoutManager(
...     repository['d']).checkout()
>>> related = zeit.cms.related.interfaces.IRelatedContent(checked_out)
>>> related.related = (repository['c'],)

Nothing has been indexed so far:

>>> sorted(relations.get_relations(repository['c']))
[]

Check in:

>>> b = zeit.cms.checkout.interfaces.ICheckinManager(checked_out).checkin()

The relation can be queried now:

>>> res = sorted(relations.get_relations(repository['c']))
>>> len(res)
1
>>> res[0].uniqueId
'http://xml.zeit.de/d'


Adding
------

Objects are index when they are first added to the repository. (Most content
types are checked out immediately after create, but that's rather accidental,
so we probably shouldn't rely on it here).

>>> new = ExampleContentType()
>>> related = zeit.cms.related.interfaces.IRelatedContent(new)
>>> related.related = (repository['e'],)
>>> repository['new'] = new
>>> res = sorted(relations.get_relations(repository['e']))
>>> len(res)
1
>>> res[0].uniqueId
'http://xml.zeit.de/new'

