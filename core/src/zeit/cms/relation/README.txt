Relations
=========

The relation support is there to answer the question by which objects an object
is referenced by, i.e. to resolve back references. The backreferences are
extrinsict, the referenced object doesn't know about them. The actualy
references are usually intrinsict, i.e. the referencing object knows it
references the other object.


Low level support
+++++++++++++++++

The `IRelations`-Utility handles all the magic of resolving
references[#functionaltest]_:

>>> import zeit.cms.relation.interfaces
>>> relations = zope.component.getUtility(
...     zeit.cms.relation.interfaces.IRelations)
>>> relations
<zeit.cms.relation.relation.Relations object at 0x...>

[#interface]_ 


Get a testcontent [#createtestcontent]_:

>>> a = repository['a']

Before asking for relations the content must be indexed:

>>> relations.index(a)

The content doesn't have any relateds currently, nor is it related anywhere:

>>> sorted(relations.get_relations(a, 'related'))
[]

Relate b and c to a via IRelatedContent

>>> related = zeit.cms.content.interfaces.IRelatedContent(a)
>>> related.related = (repository['b'], repository['c'])
>>> repository['a'] = a
>>> relations.index(a)
>>> relations.index(repository['b'])
>>> relations.index(repository['c'])

We could ask for b's relations:

>>> res = sorted(relations.get_relations(repository['b'], 'related'))
>>> len(res)
1
>>> res
[<zeit.cms.testcontenttype.testcontenttype.TestContentType object at 0x...>]
>>> res[0].uniqueId
u'http://xml.zeit.de/a'

The same accounts for c:

>>> res = sorted(relations.get_relations(repository['c'], 'related'))
>>> res[0].uniqueId
u'http://xml.zeit.de/a'


Note that `get_relations` is not transitive. So if d references a, askind for
c's references will still just yield a:

>>> d = repository['d']
>>> related = zeit.cms.content.interfaces.IRelatedContent(d)
>>> related.related = (repository['a'],)
>>> repository['d'] = d
>>> relations.index(d)

>>> res = sorted(relations.get_relations(repository['c'], 'related'))
>>> len(res)
1
>>> res[0].uniqueId
u'http://xml.zeit.de/a'


When we remove a from the repository, but do not update the index, c will no
longer reference a anyway (because we cannot find a anymore)

>>> del repository['a']
>>> sorted(relations.get_relations(repository['c'], 'related'))
[]




Event handlers
++++++++++++++

The event handlers listen on various events from `zeit.cms` and keep the
relations uptodate.

Checkin
-------

Objects are indexed before checkin. We will check a out and back in and verify
it is indexed[#cleancatalog]_. Let a relate checkout and relate
c[#needs-interaction]_:

>>> import zeit.cms.checkout.interfaces
>>> checked_out = zeit.cms.checkout.interfaces.ICheckoutManager(
...     repository['d']).checkout()
>>> related = zeit.cms.content.interfaces.IRelatedContent(checked_out)
>>> related.related = (repository['c'],)

Nothing has been indexed so far:

>>> sorted(relations.get_relations(repository['c'], 'related'))
[]

Check in:

>>> b = zeit.cms.checkout.interfaces.ICheckinManager(checked_out).checkin()

The relation can be queried now:

>>> res = sorted(relations.get_relations(repository['c'], 'related'))
>>> len(res)
1
>>> res[0].uniqueId
u'http://xml.zeit.de/d'


Updating related metadata
-------------------------

After an object was checked in which is related by other objects, the other
object's metadata is updated automatically.

Q: Should we do this asynchronously via remotetask? This might be a good choice
especially when there are many objects relating. On the other hand, the user
might want to update a channel...  let's decide that later.

Add another relation from b to c, so that updateing c will update a and b:

>>> checked_out = zeit.cms.checkout.interfaces.ICheckoutManager(
...     repository['b']).checkout()
>>> related = zeit.cms.content.interfaces.IRelatedContent(checked_out)
>>> related.related = (repository['c'],)
>>> b = zeit.cms.checkout.interfaces.ICheckinManager(checked_out).checkin()
>>> relations.index(b)


Update the teaserTitle of c:

>>> c = zeit.cms.checkout.interfaces.ICheckoutManager(
...     repository['c']).checkout()
>>> c.teaserTitle = 'Tease me'


Check c in:

>>> c = zeit.cms.checkout.interfaces.ICheckinManager(c).checkin()

The xml structure of a and b contain "Tease me" now:

>>> import lxml.etree
>>> print lxml.etree.tostring(repository['d'].xml, pretty_print=True)
<testtype xmlns:py="http://codespeak.net/lxml/objectify/pytype">
    ...
    <references>
      <reference xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" type="intern" href="http://xml.zeit.de/c" year="None" issue="None">
        <title py:pytype="str">Tease me</title>
        <description xsi:nil="true"/>
        ...
      </reference>
    </references>
    ...

>>> print lxml.etree.tostring(repository['b'].xml, pretty_print=True)
<testtype xmlns:py="http://codespeak.net/lxml/objectify/pytype">
    ...
    <references>
      <reference xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" type="intern" href="http://xml.zeit.de/c" year="None" issue="None">
        <title py:pytype="str">Tease me</title>
        <description xsi:nil="true"/>
        ...
      </reference>
    </references>
    ...


We need to make sure that we don't run into an infinte loop when we have
circular references. Let c relate to b

>>> c = zeit.cms.checkout.interfaces.ICheckoutManager(
...     repository['c']).checkout()
>>> related = zeit.cms.content.interfaces.IRelatedContent(c)
>>> related.related = (b, )

And check in:

>>> c = zeit.cms.checkout.interfaces.ICheckinManager(c).checkin()
>>> print lxml.etree.tostring(repository['b'].xml, pretty_print=True)
<testtype xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  ...
    <references>
      <reference xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" type="intern" href="http://xml.zeit.de/c" year="None" issue="None">
        <title py:pytype="str">Tease me</title>
        <description xsi:nil="true"/>
        ...
      </reference>
    </references>
    ...

>>> print lxml.etree.tostring(repository['c'].xml, pretty_print=True)
<testtype xmlns:py="http://codespeak.net/lxml/objectify/pytype">
    ...
    <references>
      <reference xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" type="intern" href="http://xml.zeit.de/b" year="None" issue="None">
        <title xsi:nil="true"/>
        <description xsi:nil="true"/>
        ...
      </reference>
    </references>
    ...


>>> zope.app.component.hooks.setSite(old_site)
>>> zope.security.management.endInteraction()

.. [#functionaltest] Setup functional test and get some common utilities

    >>> import zope.app.component.hooks
    >>> old_site = zope.app.component.hooks.getSite()
    >>> zope.app.component.hooks.setSite(getRootFolder())

    >>> import zope.component
    >>> import zeit.cms.repository.interfaces
    >>> repository = zope.component.getUtility(
    ...     zeit.cms.repository.interfaces.IRepository)

.. [#interface] Verify the interface:

    >>> import zope.interface.verify
    >>> zope.interface.verify.verifyObject(
    ...     zeit.cms.relation.interfaces.IRelations, relations)
    True


.. [#createtestcontent] Create some testcontent:

    >>> from zeit.cms.testcontenttype.testcontenttype import TestContentType

    >>> repository['a'] = TestContentType()
    >>> repository['b'] = TestContentType()
    >>> repository['c'] = TestContentType()
    >>> repository['d'] = TestContentType()

.. [#cleancatalog] Clean the catalog:

    >>> for name in ('a', 'b', 'c', 'd'):
    ...     relations._catalog.unindex_doc(
    ...         'http://xml.zeit.de/%s' % name)

.. [#needs-interaction] 

    >>> import zope.security.management
    >>> import zope.security.testing
    >>> import zope.publisher.browser
    >>> request = zope.publisher.browser.TestRequest()
    >>> request.setPrincipal(zope.security.testing.Principal(u'hans'))
    >>> zope.security.management.newInteraction(request)
