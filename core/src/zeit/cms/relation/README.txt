Relations
=========

The relation support is there to answer the question by which objects an object
is referenced by, i.e. to resolve back references. The backreferences are
extrinsic, the referenced object doesn't know about them. The actual
references are usually intrinsic, i.e. the referencing object knows it
references the other object.


Low level support
+++++++++++++++++

The `IRelations`-Utility handles all the magic of resolving
references[#functional]_:

>>> import zeit.cms.relation.interfaces
>>> relations = zope.component.getUtility(
...     zeit.cms.relation.interfaces.IRelations)
>>> relations
<zeit.cms.relation.relation.Relations object at 0x...>

[#interface]_


Get a testcontent[#createtestcontent]_:

>>> a = repository['a']

The content doesn't have any relateds currently, nor is it related anywhere:

>>> sorted(relations.get_relations(a))
[]

Relate b and c to a via IRelatedContent

>>> import zeit.cms.related.interfaces
>>> related = zeit.cms.related.interfaces.IRelatedContent(a)
>>> related.related = (repository['b'], repository['c'])
>>> repository['a'] = a

We could ask for b's relations:

>>> res = sorted(relations.get_relations(repository['b']))
>>> len(res)
1
>>> res
[<zeit.cms.testcontenttype.testcontenttype.TestContentType object at 0x...>]
>>> res[0].uniqueId
u'http://xml.zeit.de/a'

The same accounts for c:

>>> res = sorted(relations.get_relations(repository['c']))
>>> res[0].uniqueId
u'http://xml.zeit.de/a'


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
u'http://xml.zeit.de/a'

[#none-unique-id-yields-nothing]_

When we remove a from the repository, but do not update the index, c will no
longer reference a anyway (because we cannot find a anymore)

>>> del repository['a']
>>> sorted(relations.get_relations(repository['c']))
[]


.. [#none-unique-id-yields-nothing] When an object with a unique id of "None"
    is queried, nothing will be returned:

    >>> no_uid = TestContentType()
    >>> sorted(relations.get_relations(no_uid))
    []


Event handlers
++++++++++++++

The event handlers listen on various events from `zeit.cms` and keep the
relations uptodate.

Checkin
-------

Objects are indexed before checkin. We will check a out and back in and verify
it is indexed[#cleancatalog]_. Let a relate checkout and relate
c[#needsinteraction]_:

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
>>> related = zeit.cms.related.interfaces.IRelatedContent(checked_out)
>>> related.related = (repository['c'],)
>>> b = zeit.cms.checkout.interfaces.ICheckinManager(checked_out).checkin()
>>> relations.index(b)


Update the teaserTitle of c:

>>> c = zeit.cms.checkout.interfaces.ICheckoutManager(
...     repository['c']).checkout()
>>> c.teaserTitle = 'Tease me'


Check c in and "process":

>>> c = zeit.cms.checkout.interfaces.ICheckinManager(c).checkin()
>>> import gocept.async.tests
>>> gocept.async.tests.process('events')

The xml structure of a and b contain "Tease me" now:

>>> import lxml.etree
>>> print lxml.etree.tostring(repository['d'].xml, pretty_print=True)
<testtype xmlns:py="http://codespeak.net/lxml/objectify/pytype">
    ...
    <references>
      <reference ...href="http://xml.zeit.de/c"...>
        <supertitle xsi:nil="true"/>
        <title py:pytype="str">Tease me</title>
        <text xsi:nil="true"/>
        <description xsi:nil="true"/>
        <byline xsi:nil="true"/>...
      </reference>
    </references>
    ...

>>> print lxml.etree.tostring(repository['b'].xml, pretty_print=True)
<testtype xmlns:py="http://codespeak.net/lxml/objectify/pytype">
    ...
    <references>
      <reference ...href="http://xml.zeit.de/c"...>
        <supertitle xsi:nil="true"/>
        <title py:pytype="str">Tease me</title>
        <text xsi:nil="true"/>
        <description xsi:nil="true"/>
        <byline xsi:nil="true"/>...
      </reference>
    </references>
    ...


We need to make sure that we don't run into an infinte loop when we have
circular references. Let c relate to b and change something:

>>> c = zeit.cms.checkout.interfaces.ICheckoutManager(
...     repository['c']).checkout()
>>> related = zeit.cms.related.interfaces.IRelatedContent(c)
>>> related.related = (b, )
>>> c.teaserTitle = u'Tease me gently.'

And check in:

>>> c = zeit.cms.checkout.interfaces.ICheckinManager(c).checkin()
>>> gocept.async.tests.process('events')
>>> print lxml.etree.tostring(repository['b'].xml, pretty_print=True)
<testtype xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  ...
    <references>
      <reference ...href="http://xml.zeit.de/c"...>
        <supertitle xsi:nil="true"/>
        <title py:pytype="str">Tease me gently.</title>
        <text xsi:nil="true"/>
        <description xsi:nil="true"/>
        <byline xsi:nil="true"/>...
      </reference>
    </references>
    ...

>>> print lxml.etree.tostring(repository['c'].xml, pretty_print=True)
<testtype xmlns:py="http://codespeak.net/lxml/objectify/pytype">
    ...
    <references>
      <reference ...href="http://xml.zeit.de/b"...>
        <supertitle xsi:nil="true"/>
        <title xsi:nil="true"/>
        <text xsi:nil="true"/>
        <description xsi:nil="true"/>
        <byline xsi:nil="true"/>...
      </reference>
    </references>
    ...


When an object is locked or cannot be checked out due to other reasons a
message is send to the user (via flashmessage).


Verify the source of "d" before we do anything:

>>> print lxml.etree.tostring(repository['d'].xml, pretty_print=True)
<testtype xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <head>
    <references>
      <reference ...href="http://xml.zeit.de/c"...>
        <supertitle xsi:nil="true"/>
        <title py:pytype="str">Tease me gently.</title>
        <text xsi:nil="true"/>
        <description xsi:nil="true"/>
        <byline xsi:nil="true"/>...
      </reference>
    </references>
    ...
  </head>
  <body/>
</testtype>

Lock "d" by checking it out:

>>> checked_out = zeit.cms.checkout.interfaces.ICheckoutManager(
...     repository['d']).checkout()

Check out "c" and modify it. Then check in.

>>> checked_out = zeit.cms.checkout.interfaces.ICheckoutManager(
...     repository['c']).checkout()
>>> checked_out.teaserTitle = 'New teaser title'
>>> c = zeit.cms.checkout.interfaces.ICheckinManager(checked_out).checkin()
>>> gocept.async.tests.process('events')

"d" has not changed:

>>> print lxml.etree.tostring(repository['d'].xml, pretty_print=True)
<testtype xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <head>
    <references>
      <reference ...href="http://xml.zeit.de/c"...>
        <supertitle xsi:nil="true"/>
        <title py:pytype="str">Tease me gently.</title>
        <text xsi:nil="true"/>
        <description xsi:nil="true"/>
        <byline xsi:nil="true"/>...
      </reference>
    </references>
    ...
  </head>
  <body/>
</testtype>


Check out and in again:

>>> checked_out = zeit.cms.checkout.interfaces.ICheckoutManager(
...     repository['c']).checkout()
>>> checked_out.teaserTitle = 'Even newer teaser title'
>>> c = zeit.cms.checkout.interfaces.ICheckinManager(checked_out).checkin()

"d" has again not changed:

>>> print lxml.etree.tostring(repository['d'].xml, pretty_print=True)
<testtype xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <head>
    <references>
      <reference ...href="http://xml.zeit.de/c"...>
        <supertitle xsi:nil="true"/>
        <title py:pytype="str">Tease me gently.</title>
        <text xsi:nil="true"/>
        <description xsi:nil="true"/>
        <byline xsi:nil="true"/>...
      </reference>
    </references>
    ...
  </head>
  <body/>
</testtype>

Clean up:


.. [#functional] Setup functional test and get some common utilities

    >>> import zeit.cms.testing
    >>> zeit.cms.testing.set_site()

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


.. [#needsinteraction]

    >>> import zeit.cms.testing
    >>> principal = zeit.cms.testing.create_interaction()
