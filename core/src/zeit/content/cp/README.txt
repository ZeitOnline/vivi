Centerpage
==========

>>> import zeit.content.cp.centerpage
>>> cp = zeit.content.cp.centerpage.CenterPage()
>>> cp
<zeit.content.cp.centerpage.CenterPage object at 0x...>


A centerpage has three editable areas:

>>> cp['lead']
<zeit.content.cp.area.LeadRegion for lead>
>>> cp['informatives']
<zeit.content.cp.area.Region for informatives>
>>> cp['teaser-mosaic']
<zeit.content.cp.area.Cluster for teaser-mosaic>

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

Boxes
+++++

A box is part of an area. 

Placeholder box
---------------

There is a special box which can easily replaced by another box. It is a
placeholder for other boxes. This allows removing of real boxes in the teaser
mosaic without moving other boxes around. It also allows a generic "add" action
in the other areas where a placeholder is just added to the boxes and
afterwards configured.

Boxes are created using a box factory:

>>> lead = cp['lead']
>>> import zeit.content.cp.interfaces
>>> import zope.component
>>> factory = zope.component.getAdapter(
...     lead, zeit.content.cp.interfaces.IBoxFactory, name='placeholder')
>>> factory.title is None
True
>>> box = factory()
>>> box 
<zeit.content.cp.box.PlaceHolder object at 0x...>


Teaser box
----------

>>> lead = cp['lead']
>>> import zeit.content.cp.interfaces
>>> import zope.component
>>> factory = zope.component.getAdapter(
...     lead, zeit.content.cp.interfaces.IBoxFactory, name='teaser')
>>> factory.title
u'List of teasers'
>>> box = factory()
>>> box 
<zeit.content.cp.teaser.TeaserList object at 0x...>
>>> box.type
'teaser'

After calling the factory a corresponding XML node has been created:

>>> import lxml.etree
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

>>> lead[box.__name__]
<zeit.content.cp.teaser.TeaserList object at 0x...>

The area can also be iterated:

>>> list(lead.itervalues())
[<zeit.content.cp.box.PlaceHolder object at 0x...>,
 <zeit.content.cp.teaser.TeaserList object at 0x...>]
>>> lead.values()
[<zeit.content.cp.box.PlaceHolder object at 0x...>,
 <zeit.content.cp.teaser.TeaserList object at 0x...>]

It is possible to get the center page from the box by adapting to ICenterPage:

>>> zeit.content.cp.interfaces.ICenterPage(box)
<zeit.content.cp.centerpage.CenterPage object at 0x...>

The ``__parent__`` of a box is the area:

>>> box.__parent__
<zeit.content.cp.area.LeadRegion for lead>


Boxes can be removed using __delitem__:

>>> transaction.commit()
>>> len(lead)
2
>>> del lead[box.__name__]
>>> len(lead)
1
>>> lead.values()
[<zeit.content.cp.box.PlaceHolder object at 0x...>]
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
...     mosaic, zeit.content.cp.interfaces.IBoxFactory, name='teaser-bar')
>>> bar = factory()
>>> bar
<zeit.content.cp.area.TeaserBar object at 0x...>
>>> mosaic.values()
[<zeit.content.cp.area.TeaserBar object at 0x...>]
>>> cp._p_changed
True


The bar is alreay populated with four placeholders:

>>> len(bar)
4
>>> bar.values()
[<zeit.content.cp.box.PlaceHolder object at 0x...>,
 <zeit.content.cp.box.PlaceHolder object at 0x...>,
 <zeit.content.cp.box.PlaceHolder object at 0x...>,
 <zeit.content.cp.box.PlaceHolder object at 0x...>]


The xml of the teaser bar is actually a region:

>>> print lxml.etree.tostring(bar.xml, pretty_print=True),
<region ...>
  <container cp:type="placeholder" cp:__name__="<GUID>"/>
  <container cp:type="placeholder" cp:__name__="<GUID>"/>
  <container cp:type="placeholder" cp:__name__="<GUID>"/>
  <container cp:type="placeholder" cp:__name__="<GUID>"/>
</region>


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
