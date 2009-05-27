Centerpage
==========

[#functional]_

>>> import zeit.content.cp.centerpage
>>> cp = zeit.content.cp.centerpage.CenterPage()
>>> cp
<zeit.content.cp.centerpage.CenterPage object at 0x...>
>>> cp.type is None
True
>>> cp.type = u'homepage'


A centerpage has three editable areas:

>>> cp['lead']
<zeit.content.cp.area.Lead object at 0x...>
>>> cp['informatives']
<zeit.content.cp.area.Informatives object at 0x...>
>>> cp['teaser-mosaic']
<zeit.content.cp.area.Mosaic object at 0x...>

They are represented in XML as:

>>> import lxml.etree
>>> print lxml.etree.tostring(cp.xml, pretty_print=True)
<centerpage... type="homepage"...>
  <head/>
  <body>
    <cluster area="feature">
      <region area="lead"/>
      <region area="informatives"/>
    </cluster>
    <cluster area="teaser-mosaic"/>
  </body>
</centerpage>


Other areas are not accessible:

>>> cp['ugc-bar']
Traceback (most recent call last):
    ...
KeyError: 'ugc-bar'

The centerpage is reachable via ``__parent__`` or by adapting to it:

>>> cp['informatives'].__parent__
<zeit.content.cp.centerpage.CenterPage object at 0x...>
>>> zeit.content.cp.interfaces.ICenterPage(cp['informatives'])
<zeit.content.cp.centerpage.CenterPage object at 0x...>

[#modified-handler]_


Blocks
+++++

A block is part of an area.

Placeholder block
-----------------

There is a special block which can easily replaced by another block. It is a
placeholder for other blocks. This allows removing of real blocks in the teaser
mosaic without moving other blocks around. It also allows a generic "add" action
in the other areas where a placeholder is just added to the blocks and
afterwards configured.

Blocks are created using a block factory:

>>> lead = cp['lead']
>>> import zeit.content.cp.interfaces
>>> import zope.component
>>> factory = zope.component.getAdapter(
...     lead, zeit.content.cp.interfaces.IElementFactory, name='placeholder')
>>> factory.title is None
True
>>> block = factory()
>>> block
<zeit.content.cp.blocks.placeholder.PlaceHolder object at 0x...>

Creating the block automatically adds it to the container:

>>> block.__name__ in lead
True

It is not possible to add the block again:

>>> lead.add(block)
Traceback (most recent call last):
    ...
DuplicateIDError: '6ec3b591-6415-47bc-b521-d40b16c5df89'


Teaser block
------------

>>> lead = cp['lead']
>>> import zeit.content.cp.interfaces
>>> import zope.component
>>> factory = zope.component.getAdapter(
...     lead, zeit.content.cp.interfaces.IElementFactory, name='teaser')
>>> factory.title
u'List of teasers'
>>> block = factory()
>>> block
<zeit.content.cp.blocks.teaser.TeaserBlock object at 0x...>
>>> block.type
'teaser'

After calling the factory a corresponding XML node has been created:

>>> print lxml.etree.tostring(lead.xml, pretty_print=True),
<region ...
  area="lead">
  <container
    cp:type="placeholder"
    cp:__name__="..."/>
  <container
    cp:type="teaser"
    cp:__name__="..."/>
</region>


Modules are accessible via __getitem__ [#invalid-raises-error]_:

>>> lead[block.__name__]
<zeit.content.cp.blocks.teaser.TeaserBlock object at 0x...>

The area can also be iterated:

>>> list(lead.itervalues())
[<zeit.content.cp.blocks.placeholder.PlaceHolder object at 0x...>,
 <zeit.content.cp.blocks.teaser.TeaserBlock object at 0x...>]
>>> lead.values()
[<zeit.content.cp.blocks.placeholder.PlaceHolder object at 0x...>,
 <zeit.content.cp.blocks.teaser.TeaserBlock object at 0x...>]

It is possible to get the center page from the block by adapting to ICenterPage:

>>> zeit.content.cp.interfaces.ICenterPage(block)
<zeit.content.cp.centerpage.CenterPage object at 0x...>

The ``__parent__`` of a block is the area:

>>> block.__parent__
<zeit.content.cp.area.Lead object at 0x...>


Areas support ordering of their contents via the ``updateOrder`` method:

>>> transaction.commit()
>>> ph_key, block_key = lead.keys()
>>> block.__name__ == block_key
True
>>> lead.updateOrder([block_key, ph_key])
>>> lead.keys() == [block_key, ph_key]
True
>>> cp._p_changed
True

The keys have not changed:

>>> block.__name__ == block_key
True


[#invalid-arguments-to-updateorder]_

Blocks can be removed using __delitem__:

>>> transaction.commit()
>>> len(lead)
2
>>> del lead[block.__name__]
>>> len(lead)
1
>>> lead.values()
[<zeit.content.cp.blocks.placeholder.PlaceHolder object at 0x...>]
>>> cp._p_changed
True


Teaser mosaic
+++++++++++++

The teaser mosaic contains teaser bars. Note that the term *teaser* mosaic is
missleading as it may also contain a lot of other things (like information
about the weather).

>>> transaction.commit()
>>> mosaic = cp['teaser-mosaic']
>>> factory = zope.component.getAdapter(
...     mosaic, zeit.content.cp.interfaces.IElementFactory, name='teaser-bar')
>>> bar = factory()
>>> bar
<zeit.content.cp.blocks.teaserbar.TeaserBar object at 0x...>
>>> mosaic.values()
[<zeit.content.cp.blocks.teaserbar.TeaserBar object at 0x...>]
>>> cp._p_changed
True


The bar is alreay populated with four placeholders:

>>> len(bar)
4
>>> bar.values()
[<zeit.content.cp.blocks.placeholder.PlaceHolder object at 0x...>,
 <zeit.content.cp.blocks.placeholder.PlaceHolder object at 0x...>,
 <zeit.content.cp.blocks.placeholder.PlaceHolder object at 0x...>,
 <zeit.content.cp.blocks.placeholder.PlaceHolder object at 0x...>]


The xml of the teaser bar is actually a region:

>>> print lxml.etree.tostring(bar.xml, pretty_print=True),
<region ...>
  <container cp:type="placeholder" cp:__name__="<GUID>"/>
  <container cp:type="placeholder" cp:__name__="<GUID>"/>
  <container cp:type="placeholder" cp:__name__="<GUID>"/>
  <container cp:type="placeholder" cp:__name__="<GUID>"/>
</region>


Teaser mosaic layouts
+++++++++++++++++++++

(analog to blocks/teaser.txt/Layouts)

>>> import zeit.content.cp.layout
>>> bar.layout = zeit.content.cp.layout.get_layout('dmr')
>>> print lxml.etree.tostring(bar.xml, pretty_print=True)
<region...module="dmr"...


Checkin handler
+++++++++++++++

When the centerpage is checked in, the metadata of all its articles need to be
updated [#needsinteraction]_.

Before we can begin, we need to put our centerpage into the repository so that
we can check it out:

>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)
>>> repository['cp'] = cp
>>> cp = zeit.cms.checkout.interfaces.ICheckoutManager(
...     repository['cp']).checkout()

Now we need some test objects we can edit later on:

>>> factory = zope.component.getAdapter(
...     cp['lead'], zeit.content.cp.interfaces.IElementFactory, name='teaser')
>>> teasers = factory()
>>> import zeit.cms.repository.interfaces
>>> teaser = zeit.content.cp.teaser.Teaser()
>>> teaser.original_content = repository['testcontent']
>>> teaser = repository['testcontent-1'] = teaser
>>> teasers.insert(0, repository['testcontent'])
>>> teasers.insert(1, teaser)

Edit the referenced article while the centerpage is checked out:

>>> testcontent = zeit.cms.checkout.interfaces.ICheckoutManager(
...     repository['testcontent']).checkout()
>>> testcontent.teaserTitle = 'Foo'
>>> dummy = zeit.cms.checkout.interfaces.ICheckinManager(testcontent).checkin()

When we now check in the centerpage, the changes in our article are propagated.
We also check that the teaser object contains a link to its original article:

>>> cp = zeit.cms.checkout.interfaces.ICheckinManager(cp).checkin()
>>> print lxml.etree.tostring(cp.xml, pretty_print=True)
<centerpage ...
<block href="http://xml.zeit.de/testcontent"...
  <title py:pytype="str">Foo</title>...
<block xmlns:ns0="http://namespaces.zeit.de/CMS/link"
       href="http://xml.zeit.de/testcontent-1"
       ns0:href="http://xml.zeit.de/testcontent">...


.. [#needsinteraction]

    >>> principal = zeit.cms.testing.create_interaction()


.. [#functional]

    >>> import zeit.cms.testing
    >>> zeit.cms.testing.set_site()


.. [#modified-handler] The centerpages need to be nodified when sub location
    change. When we modify an area the centerpage will be considered changed:

    >>> import transaction
    >>> import zope.event
    >>> import zope.lifecycleevent
    >>> getRootFolder()['cp'] = cp
    >>> transaction.commit()  # Commit to actually be able to "change"
    >>> zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(
    ...     cp['lead']))
    >>> cp._p_changed
    True

    There is also such a handler for IObjectMovedEvent:

    >>> transaction.commit()
    >>> import zope.container.contained
    >>> zope.event.notify(zope.container.contained.ObjectMovedEvent(
    ...     cp['lead'], None, None, None, None))
    >>> cp._p_changed
    True


.. [#invalid-raises-error]

    >>> lead['foo']
    Traceback (most recent call last):
        ...
    KeyError: 'foo'

.. [#invalid-arguments-to-updateorder] Invalid arguments to update order raise
    errors as defined in the interface:

    >>> lead.updateOrder(124)
    Traceback (most recent call last):
        ...
    TypeError: order must be tuple or list, got <type 'int'>.

    >>> lead.updateOrder(['abc', 'def'])
    Traceback (most recent call last):
        ...
    ValueError: order must have the same keys.



