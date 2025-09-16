=======================
Images and image groups
=======================

Images contain the image data and some metadata. An image group contains
several images.

>>> import transaction
>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()
>>> principal = zeit.cms.testing.create_interaction()
>>> import zope.component

Image group
===========

XML reference
+++++++++++++

Create an image group first:

>>> import zeit.cms.repository.interfaces
>>> repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
>>> group = repository['group']

Reference the image via XML:

>>> import zeit.cms.content.interfaces
>>> ref = zope.component.getAdapter(
...     group,
...     zeit.cms.content.interfaces.IXMLReference, name='image')
>>> print(zeit.cms.testing.xmltotext(ref))
<image base-id="http://xml.zeit.de/group" type="jpg"/>


Set metadata:

>>> import zeit.cms.checkout.interfaces
>>> group = zeit.cms.checkout.interfaces.ICheckoutManager(group).checkout()
>>> metadata = zeit.content.image.interfaces.IImageMetadata(group)
>>> metadata.copyright = (
...     ('Agentur XY', 'http://xyz.de'))
>>> metadata.caption = 'Caption'
>>> group = zeit.cms.checkout.interfaces.ICheckinManager(group).checkin()
>>> transaction.commit()
>>> ref = zope.component.getAdapter(
...     group,
...     zeit.cms.content.interfaces.IXMLReference, name='image')
>>> print(zeit.cms.testing.xmltotext(ref))
<image base-id="http://xml.zeit.de/group" type="jpg"/>

The interface default for the copyright is None:

>>> zeit.content.image.interfaces.IImageMetadata['copyright'].default


Make sure we don't die when there is an invalid XML snippet stored:

>>> group = zeit.cms.checkout.interfaces.ICheckoutManager(group).checkout()
>>> properties = zeit.connector.interfaces.IWebDAVProperties(group)
>>> properties[('caption', 'http://namespaces.zeit.de/CMS/image')] = '5 < 7'
>>> group = zeit.cms.checkout.interfaces.ICheckinManager(group).checkin()
>>> ref = zope.component.getAdapter(
...     group,
...     zeit.cms.content.interfaces.IXMLReference, name='image')
>>> print(zeit.cms.testing.xmltotext(ref))
<image base-id="http://xml.zeit.de/group" type="jpg"/>

Set the link:

>>> transaction.commit()
>>> group = zeit.cms.checkout.interfaces.ICheckoutManager(group).checkout()
>>> meta = zeit.content.image.interfaces.IImageMetadata(group)
>>> meta.links_to = 'http://www.asdf.com'
>>> meta.nofollow = True
>>> group = zeit.cms.checkout.interfaces.ICheckinManager(group).checkin()
>>> ref = zope.component.getAdapter(
...     group,
...     zeit.cms.content.interfaces.IXMLReference, name='image')
>>> print(zeit.cms.testing.xmltotext(ref))
<image base-id="http://xml.zeit.de/group" type="jpg"/>

The type attribute is rather complex.

Case 1 is simple, we've seen it above: When there is only one extension it's
used as type.

Case 2: When there is a mix of formats the type of an image whose name ends
in x140 is used:

>>> image = zeit.content.image.image.LocalImage()
>>> with image.open('w') as f:
...     _ = f.write(b'foo')
>>> group['title-120x140.gif'] = image
>>> ref = zope.component.getAdapter(
...     group,
...     zeit.cms.content.interfaces.IXMLReference, name='image')
>>> print(zeit.cms.testing.xmltotext(ref))
<image base-id="http://xml.zeit.de/group" type="gif"/>


Case 3: When there is a mix of formats and no image ends in x140 the "first"
one is used:

>>> del group['title-120x140.gif']
>>> image = zeit.content.image.image.LocalImage()
>>> with image.open('w') as f:
...     _ = f.write(b'bar')
>>> group['title-120x120.gif'] = image
>>> ref = zope.component.getAdapter(
...     group,
...     zeit.cms.content.interfaces.IXMLReference, name='image')
>>> print(zeit.cms.testing.xmltotext(ref))
<image base-id="http://xml.zeit.de/group" type="jpg"/>


Images whose names have no extension at all will be ignored:


>>> image = zeit.content.image.image.LocalImage()
>>> with image.open('w') as f:
...     _ = f.write(b'blubs')
>>> group['title-120x140'] = image
>>> ref = zope.component.getAdapter(
...     group,
...     zeit.cms.content.interfaces.IXMLReference, name='image')
>>> print(zeit.cms.testing.xmltotext(ref))
<image base-id="http://xml.zeit.de/group" type="jpg"/>

If there is no image in the image group the ``type`` will be an empty string:

>>> for name in group:
...     if not name.startswith('thumbnail'):
...         del group[name]
>>> ref = zope.component.getAdapter(
...     group,
...     zeit.cms.content.interfaces.IXMLReference, name='image')
>>> print(zeit.cms.testing.xmltotext(ref))
<image base-id="http://xml.zeit.de/group" type=""/>


There is also a view for the metadata:

>>> zope.component.getMultiAdapter((group, object()), name='metadata')
<zeit.content.image.metadata.ImageMetadata object at 0x...>
