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
<centerpage... type="homepage"...>
  <head>...
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

>>> cp['ugc-bar']
Traceback (most recent call last):
    ...
KeyError: 'ugc-bar'

The centerpage is reachable via ``__parent__`` or by adapting to it:

>>> cp['feature'].__parent__
<zeit.content.cp.centerpage.Body...>
>>> import zeit.content.cp.interfaces
>>> zeit.content.cp.interfaces.ICenterPage(cp['feature'])
<zeit.content.cp.centerpage.CenterPage...>


The centerpages need to be nodified when sub location change. When we modify an
area the centerpage will be considered changed:

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

>>> import zope.container.contained
>>> zope.event.notify(zope.container.contained.ObjectMovedEvent(
...     cp['lead'], None, None, None, None))
>>> cp._p_changed
True


Header image
++++++++++++

>>> import zeit.cms.repository.interfaces
>>> import zope.component
>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)
>>> cp.header_image = repository['2006']['DSC00109_2.JPG']
>>> print(zeit.cms.testing.xmltotext(cp.xml))
<centerpage...>
<head>
...
<header_image src="http://xml.zeit.de/2006/DSC00109_2.JPG"...>
...
</centerpage>


OG-Metadata
+++++++++++

>>> cp.og_title = 'Isch bin da Title'
>>> cp.og_description = 'Hier geht die Description'
>>> cp.og_image = 'yo-man.jpg'
>>> print(zeit.cms.testing.xmltotext(cp.xml))
<centerpage...>
  <head>
...
    <og_meta>
       <og_title...>Isch bin da Title</og_title>
       <og_description...>Hier geht die Description</og_description>
       <og_image...>yo-man.jpg</og_image>
    </og_meta>
  ...
</centerpage>


Blocks
++++++

A block is part of an area.

Teaser block
------------

>>> informatives = cp['informatives']
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


Checkin handler
+++++++++++++++

When the centerpage is checked in, the metadata of all its articles need to be
updated.

Before we can begin, we need to put our centerpage into the repository so that
we can check it out:

>>> principal = zeit.cms.testing.create_interaction()
>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)
>>> repository['cp'] = cp
>>> cp = zeit.cms.checkout.interfaces.ICheckoutManager(
...     repository['cp']).checkout()

Now we need some test objects we can edit later on:

>>> factory = zope.component.getAdapter(
...     cp['lead'], zeit.edit.interfaces.IElementFactory, name='teaser')
>>> teasers = factory()
>>> teasers.insert(0, repository['testcontent'])

Edit the referenced article while the centerpage is checked out:

>>> testcontent = zeit.cms.checkout.interfaces.ICheckoutManager(
...     repository['testcontent']).checkout()
>>> testcontent.teaserTitle = 'Foo'
>>> dummy = zeit.cms.checkout.interfaces.ICheckinManager(testcontent).checkin()

When we now check in the centerpage, the changes in our article are propagated.

>>> cp = zeit.cms.checkout.interfaces.ICheckinManager(cp).checkin()
>>> cp = repository['cp']
>>> print(zeit.cms.testing.xmltotext(cp.xml))
<centerpage ...
<block ...href="http://xml.zeit.de/testcontent"...
  <title>Foo</title>...


Content referenced in a centerpage has additional dates on the node:

>>> print(zeit.cms.testing.xmltotext(cp.xml))
<centerpage...
  <block ...href="http://xml.zeit.de/testcontent"...
         date-last-modified="2009-09-11T08:18:48+00:00"
         date-first-released=""
         date-last-published=""
         last-semantic-change=""...


Make a semantic change to testcontent:

>>> import zeit.cms.checkout.helper
>>> with zeit.cms.checkout.helper.checked_out(repository['testcontent'],
...                                           semantic_change=True):
...     pass

The metadata is updated (asynchronously) when the centerpage is checked in:

>>> with zeit.cms.checkout.helper.checked_out(repository['cp']):
...     pass
>>> print(zeit.cms.testing.xmltotext(repository['cp'].xml))
<centerpage...
  <block ...href="http://xml.zeit.de/testcontent"...
         date-last-modified="2009-09-11T08:18:48+00:00"
         date-first-released=""
         date-last-published=""
         last-semantic-change="2009-09-11T08:18:48+00:00"...

Publish test content:

>>> zeit.cms.workflow.interfaces.IPublishInfo(
...     repository['testcontent']).urgent = True
>>> job_id = zeit.cms.workflow.interfaces.IPublish(
...     repository['testcontent']).publish()

The data is, again, updated when the CP is checked in:

>>> with zeit.cms.checkout.helper.checked_out(repository['cp']):
...     pass
>>> print(zeit.cms.testing.xmltotext(repository['cp'].xml))
<centerpage...
  <block ...href="http://xml.zeit.de/testcontent"...
         date-last-modified="2009-09-11T08:18:48+00:00"
         date-first-released="2009-09-11T08:18:48+00:00"
         date-last-published="2009-09-11T08:18:48+00:00"
         last-semantic-change="2009-09-11T08:18:48+00:00"...
