Centerpage
==========

[#functional]_

>>> import zeit.content.cp.centerpage
>>> cp = zeit.content.cp.centerpage.CenterPage()
>>> cp
<zeit.content.cp.centerpage.CenterPage object at 0x...>
>>> cp.type = u'homepage'
>>> cp.type
u'homepage'


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
  <head>...
  <body>
    <cluster area="feature">
      <region area="lead"/>
      <region area="informatives"/>
    </cluster>
    <cluster area="teaser-mosaic"/>
  </body>
  <feed/>
</centerpage>
>>> import zeit.connector.interfaces
>>> print zeit.connector.interfaces.IWebDAVProperties(cp)[
...     ('type', 'http://namespaces.zeit.de/CMS/zeit.content.cp')]
homepage



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


Header image
++++++++++++

>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)
>>> cp.header_image = repository['2006']['DSC00109_2.JPG']
>>> print lxml.etree.tostring(cp.xml, pretty_print=True)
<centerpage...>
<head>
...
<header_image src="http://xml.zeit.de/2006/DSC00109_2.JPG"...>
...
</centerpage>


Topic Links
+++++++++++

>>> cp.topiclink_title = 'Sachsen Linkse' 
>>> cp.topiclink_label_1 = 'Sachsen spezial' 
>>> cp.topiclink_url_1 = 'http://www.zeit.de/themen/sachsen/index' 
>>> print lxml.etree.tostring(cp.xml, pretty_print=True)
<centerpage...>
  <head>
...
    <topiclinks>
      <topiclink_title...>Sachsen Linkse</topiclink_title>
      <topiclink>
        <topiclink_label_1...>Sachsen spezial</topiclink_label_1>
        <topiclink_url_1...>http://www.zeit.de/themen/sachsen/index</topiclink_url_1>
      </topiclink>
    </topiclinks>
  ...
</centerpage>


OG-Metadata
+++++++++++

>>> cp.og_title = 'Isch bin da Title' 
>>> cp.og_description = 'Hier geht die Description' 
>>> cp.og_image = 'yo-man.jpg' 
>>> print lxml.etree.tostring(cp.xml, pretty_print=True)
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

Placeholder block
-----------------

There is a special block which can easily replaced by another block. It is a
placeholder for other blocks. This allows removing of real blocks in the teaser
mosaic without moving other blocks around. It also allows a generic "add" action
in the other areas where a placeholder is just added to the blocks and
afterwards configured.

Blocks are created using a block factory:

>>> informatives = cp['informatives']
>>> import zeit.content.cp.interfaces
>>> import zope.component
>>> factory = zope.component.getAdapter(
...     informatives, zeit.content.cp.interfaces.IElementFactory,
...     name='placeholder')
>>> factory.title is None
True
>>> block = factory()
>>> block
<zeit.content.cp.blocks.placeholder.PlaceHolder object at 0x...>

Creating the block automatically adds it to the container:

>>> block.__name__ in informatives
True

It is not possible to add the block again:

>>> informatives.add(block)
Traceback (most recent call last):
    ...
DuplicateIDError: '6ec3b591-6415-47bc-b521-d40b16c5df89'


Teaser block
------------

>>> informatives = cp['informatives']
>>> import zeit.content.cp.interfaces
>>> import zope.component
>>> factory = zope.component.getAdapter(
...     informatives, zeit.content.cp.interfaces.IElementFactory,
...     name='teaser')
>>> factory.title
u'List of teasers'
>>> block = factory()
>>> block
<zeit.content.cp.blocks.teaser.AutoPilotTeaserBlock object at 0x...>
>>> block.type
'teaser'

After calling the factory a corresponding XML node has been created:

>>> print lxml.etree.tostring(informatives.xml, pretty_print=True),
<region ... area="informatives">
  <container cp:type="placeholder" module="placeholder" cp:__name__="..."/>
  <container cp:type="teaser" module="large" ... cp:__name__="..."/>
</region>


Modules are accessible via __getitem__ [#invalid-raises-error]_:

>>> informatives[block.__name__]
<zeit.content.cp.blocks.teaser.AutoPilotTeaserBlock object at 0x...>

The area can also be iterated:

>>> list(informatives.itervalues())
[<zeit.content.cp.blocks.placeholder.PlaceHolder object at 0x...>,
 <zeit.content.cp.blocks.teaser.AutoPilotTeaserBlock object at 0x...>]
>>> informatives.values()
[<zeit.content.cp.blocks.placeholder.PlaceHolder object at 0x...>,
 <zeit.content.cp.blocks.teaser.AutoPilotTeaserBlock object at 0x...>]

It is possible to get the center page from the block by adapting to ICenterPage:

>>> zeit.content.cp.interfaces.ICenterPage(block)
<zeit.content.cp.centerpage.CenterPage object at 0x...>

The ``__parent__`` of a block is the area:

>>> block.__parent__
<zeit.content.cp.area.Informatives object at 0x...>


Areas support ordering of their contents via the ``updateOrder`` method:

>>> transaction.commit()
>>> ph_key, block_key = informatives.keys()
>>> block.__name__ == block_key
True
>>> informatives.updateOrder([block_key, ph_key])
>>> informatives.keys() == [block_key, ph_key]
True
>>> cp._p_changed
True

The keys have not changed:

>>> block.__name__ == block_key
True


[#invalid-arguments-to-updateorder]_

Blocks can be removed using __delitem__:

>>> transaction.commit()
>>> len(informatives)
2
>>> del informatives[block.__name__]
>>> len(informatives)
1
>>> informatives.values()
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
  <container cp:type="placeholder" module="placeholder" cp:__name__="<GUID>"/>
  <container cp:type="placeholder" module="placeholder" cp:__name__="<GUID>"/>
  <container cp:type="placeholder" module="placeholder" cp:__name__="<GUID>"/>
  <container cp:type="placeholder" module="placeholder" cp:__name__="<GUID>"/>
</region>


Teaser mosaic layouts
+++++++++++++++++++++

(analog to blocks/teaser.txt/Layouts)

>>> import zeit.content.cp.layout
>>> bar.layout = zeit.content.cp.layout.get_bar_layout('dmr')
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
>>> repository['testcontent-1'] = teaser
>>> teaser = repository['testcontent-1']
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
>>> import gocept.async.tests
>>> gocept.async.tests.process()
>>> cp = repository['cp']
>>> print lxml.etree.tostring(cp.xml, pretty_print=True)
<centerpage ...
<block href="http://xml.zeit.de/testcontent"...
  <title py:pytype="str">Foo</title>...
<block xmlns:ns0="http://namespaces.zeit.de/CMS/link"
       href="http://xml.zeit.de/testcontent-1"...
       ns0:href="http://xml.zeit.de/testcontent"...>...


Content referenced in a centerpage has additional dates on the node:

>>> print lxml.etree.tostring(cp.xml, pretty_print=True)
<centerpage...
  <block href="http://xml.zeit.de/testcontent"...
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
>>> gocept.async.tests.process()
>>> print lxml.etree.tostring(repository['cp'].xml, pretty_print=True)
<centerpage...
  <block href="http://xml.zeit.de/testcontent"...
         date-last-modified="2009-09-11T08:18:48+00:00"
         date-first-released=""
         date-last-published=""
         last-semantic-change="2009-09-11T08:18:48+00:00"...

Publish test content:

>>> zeit.cms.workflow.interfaces.IPublishInfo(
...     repository['testcontent']).urgent = True
>>> job_id = zeit.cms.workflow.interfaces.IPublish(
...     repository['testcontent']).publish()
>>> import lovely.remotetask.interfaces
>>> tasks = zope.component.getUtility(
...     lovely.remotetask.interfaces.ITaskService, 'general')
>>> tasks.process()

The data is, again, updated when the CP is checked in:

>>> with zeit.cms.checkout.helper.checked_out(repository['cp']):
...     pass
>>> gocept.async.tests.process()
>>> print lxml.etree.tostring(repository['cp'].xml, pretty_print=True)
<centerpage...
  <block href="http://xml.zeit.de/testcontent"...
         date-last-modified="2009-09-11T08:18:48+00:00"
         date-first-released="2009-09-11T08:18:48+00:00"
         date-last-published="2009-09-11T08:18:48+00:00"
         last-semantic-change="2009-09-11T08:18:48+00:00"...


Referenced images
+++++++++++++++++

>>> img = repository['2006']['DSC00109_2.JPG']
>>> with zeit.cms.checkout.helper.checked_out(repository['cp']) as co:
...     co.header_image = img
>>> with zeit.cms.checkout.helper.checked_out(img) as co:
...     zeit.content.image.interfaces.IImageMetadata(co).title = 'updated'
>>> gocept.async.tests.process()
>>> print lxml.etree.tostring(repository['cp'].xml, pretty_print=True)
<centerpage...
  <header_image... title="updated"...>
...

Topic page
==========


>>> topic_provider = zope.component.getUtility(
...     zeit.cms.sitecontrol.interfaces.ISitesProvider, name='topicpage')
>>> import pprint
>>> pprint.pprint(list(topic_provider))
Searching:  (:eq "http://namespaces.zeit.de/CMS/zeit.content.cp" "type" "topicpage")
[<zeit.cms.repository.unknown.PersistentUnknownResource object at 0x3a4a2f0>,
 <zeit.cms.repository.unknown.PersistentUnknownResource object at 0x3a4adf0>,
 <zeit.cms.repository.unknown.PersistentUnknownResource object at 0x3a5f4b0>]


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

    >>> informatives['foo']
    Traceback (most recent call last):
        ...
    KeyError: 'foo'

.. [#invalid-arguments-to-updateorder] Invalid arguments to update order raise
    errors as defined in the interface:

    >>> informatives.updateOrder(124)
    Traceback (most recent call last):
        ...
    TypeError: order must be tuple or list, got <type 'int'>.

    >>> informatives.updateOrder(['abc', 'def'])
    Traceback (most recent call last):
        ...
    ValueError: order must have the same keys.
