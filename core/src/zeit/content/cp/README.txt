Centerpage
==========

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()

>>> import zeit.content.cp.centerpage
>>> cp = zeit.content.cp.centerpage.CenterPage()
>>> cp
<zeit.content.cp.centerpage.CenterPage...>
>>> cp.type = 'homepage'
>>> cp.type
'homepage'


The ancient XML representation looked as follows:

>>> print(zeit.cms.testing.xmltotext(cp.xml))
<centerpage...>
  <head/>
  <body>
    <cluster area="feature" kind="duo">
      <region area="lead" kind="major"/>
      <region area="informatives" kind="minor"/>
    </cluster>
  </body>
</centerpage>
>>> import zeit.connector.interfaces
>>> print(zeit.connector.interfaces.IWebDAVProperties(cp)[
...     ('type', 'http://namespaces.zeit.de/CMS/zeit.content.cp')])
homepage



Other areas are not accessible:

>>> cp.body['ugc-bar']
Traceback (most recent call last):
    ...
KeyError: 'ugc-bar'

The centerpage is reachable via ``__parent__`` or by adapting to it:

>>> cp.body['feature'].__parent__
<zeit.content.cp.centerpage.Body...>
>>> import zeit.content.cp.interfaces
>>> zeit.content.cp.interfaces.ICenterPage(cp.body['feature'])
<zeit.content.cp.centerpage.CenterPage...>


The centerpages need to be nodified when sub location change. When we modify an
area the centerpage will be considered changed:

>>> import transaction
>>> import zope.event
>>> import zope.lifecycleevent
>>> getRootFolder()['cp'] = cp
>>> transaction.commit()  # Commit to actually be able to "change"
>>> zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(
...     cp.body['lead']))
>>> cp._p_changed
True

There is also such a handler for IObjectMovedEvent:

>>> import zope.container.contained
>>> zope.event.notify(zope.container.contained.ObjectMovedEvent(
...     cp.body['lead'], None, None, None, None))
>>> cp._p_changed
True


OG-Metadata
+++++++++++

>>> cp.og_title = 'Isch bin da Title'
>>> cp.og_description = 'Hier geht die Description'
>>> cp.og_image = 'yo-man.jpg'
>>> print(zeit.cms.testing.xmltotext(cp.xml))
<centerpage...>
  <head>
    <og_meta>
      <og_title>Isch bin da Title</og_title>
      <og_description>Hier geht die Description</og_description>
      <og_image>yo-man.jpg</og_image>
    </og_meta>
  ...
</centerpage>


Blocks
++++++

A block is part of an area.

Teaser block
------------

>>> informatives = cp.body['informatives']
>>> import zeit.content.cp.interfaces
>>> import zope.component
>>> factory = zope.component.getAdapter(
...     informatives, zeit.edit.interfaces.IElementFactory,
...     name='teaser')
>>> factory.title
'List of teasers'
>>> block = factory()
>>> block
<zeit.content.cp.blocks.teaser.TeaserBlock...>
>>> block.type
'teaser'

After calling the factory a corresponding XML node has been created:

>>> print(zeit.cms.testing.xmltotext(informatives.xml))
<region ... area="informatives"...>
  <container cp:type="teaser" module="buttons" ... cp:__name__="..."/>
</region>


Modules are accessible via __getitem__:

>>> informatives['invalid']
Traceback (most recent call last):
    ...
KeyError: 'invalid'
>>> informatives[block.__name__]
<zeit.content.cp.blocks.teaser.TeaserBlock...>

The area can also be iterated:

>>> informatives.values()
[<zeit.content.cp.blocks.teaser.TeaserBlock...>]

It is possible to get the center page from the block by adapting to ICenterPage:

>>> zeit.content.cp.interfaces.ICenterPage(block)
<zeit.content.cp.centerpage.CenterPage...>

The ``__parent__`` of a block is the area:

>>> block.__parent__
<zeit.content.cp.area.Area...>


Areas support ordering of their contents via the ``updateOrder`` method:

>>> [block_key] = informatives.keys()
>>> block.__name__ == block_key
True
>>> informatives.updateOrder([block_key])
>>> informatives.keys() == [block_key]
True
>>> cp._p_changed
True

The keys have not changed:

>>> block.__name__ == block_key
True

Invalid arguments to update order raise errors as defined in the interface:

>>> informatives.updateOrder(124)
Traceback (most recent call last):
    ...
TypeError: order must be tuple or list...

>>> informatives.updateOrder(['abc', 'def'])
Traceback (most recent call last):
    ...
ValueError: order must have the same keys.

Blocks can be removed using __delitem__:

>>> len(informatives)
1
>>> del informatives[block.__name__]
>>> len(informatives)
0
>>> informatives.values()
[]
>>> cp._p_changed
True
