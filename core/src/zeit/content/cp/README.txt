Centerpage
==========

>>> import zeit.content.cp.centerpage
>>> cp = zeit.content.cp.centerpage.CenterPage()
>>> cp
<zeit.content.cp.centerpage.CenterPage object at 0x...>


A centerpage has three editable areas:

>>> cp['lead']
<zeit.content.cp.region.Region for lead>
>>> cp['informatives']
<zeit.content.cp.region.Region for informatives>
>>> cp['teaser-mosaic']
<zeit.content.cp.region.Region for teaser-mosaic>

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

A box is part of an area. Boses are created using a box factory:

>>> lead = cp['lead']
>>> import zeit.content.cp.interfaces
>>> import zope.component
>>> factory = zope.component.getAdapter(
...     lead, zeit.content.cp.interfaces.IBoxFactory, name='teaser')
>>> factory .title
u'List of teasers'
>>> box = factory()
>>> box 
<zeit.content.cp.teaser.TeaserList object at 0x...>

After calling the factory a corresponding XML node has been created:

>>> import lxml.etree
>>> print lxml.etree.tostring(lead.xml, pretty_print=True),
<region ... 
  area="lead">
  <container
    cp:type="teaser"
    cp:__name__="..."/>
</region>


Modules are accessible via __getitem__ [#invalid-raises-error]_:

>>> lead[box.__name__]
<zeit.content.cp.teaser.TeaserList object at 0x...>

The area can also be iterated:

>>> list(lead)
[<zeit.content.cp.teaser.TeaserList object at 0x...>]

It is possible to get the center page from the box by adapting to ICenterPage:

>>> zeit.content.cp.interfaces.ICenterPage(box)
<zeit.content.cp.centerpage.CenterPage object at 0x...>

The ``__parent__`` of a box is the area:

>>> box.__parent__
<zeit.content.cp.region.Region for lead>



.. [#modified-handler] The centerpages need to be nodified when sub location
    change. When we modify an area the centerpage will be considered changed:

    >>> import zope.event
    >>> import zope.lifecycleevent
    >>> zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(
    ...     cp['lead']))

    #>>> cp._p_changed
    # XXX currently broken
    True

.. [#invalid-raises-error]

    >>> lead['foo']
    Traceback (most recent call last):
        ...
    KeyError: 'foo'
