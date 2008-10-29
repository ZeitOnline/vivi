=======================
Images and image groups
=======================

Images contain the image data and some metadata. An image group contains
several images.

Setup functional test:

>>> import zope.app.component.hooks
>>> old_site = zope.app.component.hooks.getSite()
>>> zope.app.component.hooks.setSite(getRootFolder())
>>> import zope.security.testing
>>> principal = zope.security.testing.Principal(u'zope.user')
>>> participation = zope.security.testing.Participation(principal)
>>> import zope.security.management
>>> zope.security.management.newInteraction(participation)

Image
=====

Test the image xml reference:

>>> import lxml.etree
>>> import zope.component
>>> import zeit.cms.repository.interfaces
>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)
>>> image = repository['2006']['DSC00109_2.JPG']
>>> ref = zope.component.getAdapter(
...     image,
...     zeit.cms.content.interfaces.IXMLReference, name='image')
>>> print lxml.etree.tostring(ref, pretty_print=True)
<image xmlns:py="http://codespeak.net/lxml/objectify/pytype"
  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  src="http://xml.zeit.de/2006/DSC00109_2.JPG"
  type="JPG">
  <bu xsi:nil="true"/>
  <copyright py:pytype="str">&#169;</copyright>
</image>


When the image is adapted to ILocalContent we'll get a LocalImage:

>>> image
<zeit.content.image.image.RepositoryImage object at 0x...>
>>> image.mimeType
'image/jpeg'
>>> import zeit.cms.workingcopy.interfaces
>>> local = zeit.cms.workingcopy.interfaces.ILocalContent(image)
>>> local
<zeit.content.image.image.LocalImage object at 0x...>
>>> local.__name__
u'DSC00109_2.JPG'
>>> local.mimeType
'image/jpeg'

Let's set some metadata on the local image:

>>> metadata = zeit.content.image.interfaces.IImageMetadata(local)
>>> metadata.title = 'my title'

When we make a resource from a LocalImage the contentType is set correctly:

>>> import zeit.connector.interfaces
>>> resource = zeit.connector.interfaces.IResource(local)
>>> resource.contentType
'image/jpeg'

The properties contain the title:

>>> import pprint
>>> pprint.pprint(dict(resource.properties))
{('getlastmodified', 'DAV:'): u'Fri, 07 Mar 2008 12:47:16 GMT',
 ('title', 'http://namespaces.zeit.de/CMS/document'): u'my title',
 ('type', 'http://namespaces.zeit.de/CMS/meta'): 'image'}

Le's add the local image to the repository:

>>> repository['2006']['DSC00109_2.JPG'] = local

The metadata is still there:

>>> image = repository['2006']['DSC00109_2.JPG']
>>> metadata = zeit.content.image.interfaces.IImageMetadata(image)
>>> metadata.title
u'my title'

The local image also has the title:

>>> local = zeit.cms.workingcopy.interfaces.ILocalContent(image)
>>> metadata = zeit.content.image.interfaces.IImageMetadata(local)
>>> metadata.title
u'my title'

The repository image factory returns None when the image cannot be identified:

>>> import zeit.content.image.image
>>> connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
>>> zeit.content.image.image.repositoryimage_factory(
...     connector['http://xml.zeit.de/online/2007/01/Somalia']) is None
True


Image group
===========

XML reference
+++++++++++++

Create an image group first:

>>> import zeit.cms.checkout.interfaces
>>> import zeit.content.image.test
>>> group = zeit.content.image.test.create_image_group()

Reference the image via XML:

>>> import zeit.cms.content.interfaces
>>> ref = zope.component.getAdapter(
...     group,
...     zeit.cms.content.interfaces.IXMLReference, name='image')
>>> print lxml.etree.tostring(ref, pretty_print=True)
<image xmlns:py="http://codespeak.net/lxml/objectify/pytype"
       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       base-id="http://xml.zeit.de/image-group" type="jpg">
  <bu xsi:nil="true"/>
  <copyright py:pytype="str">&#169;</copyright>
</image>


Set metadata:

>>> group = zeit.cms.checkout.interfaces.ICheckoutManager(group).checkout()
>>> metadata = zeit.content.image.interfaces.IImageMetadata(group)
>>> metadata.copyrights = (
...     ('Zeit online', None),
...     ('Agentur XY', 'http://xyz.de'))
>>> metadata.alignment = u'right'
>>> metadata.caption = u'Cap>tion<br/><a href="#">foo</a>'
>>> group = zeit.cms.checkout.interfaces.ICheckinManager(group).checkin()
>>> ref = zope.component.getAdapter(
...     group,
...     zeit.cms.content.interfaces.IXMLReference, name='image')
>>> print lxml.etree.tostring(ref, pretty_print=True)
<image xmlns:py="http://codespeak.net/lxml/objectify/pytype"
       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       align="right"
       base-id="http://xml.zeit.de/image-group" type="jpg">
  <bu>Cap&gt;tion<br/><a href="#">foo</a></bu>
  <copyright py:pytype="str">Zeit online</copyright>
  <copyright py:pytype="str" link="http://xyz.de">Agentur XY</copyright>
</image>

The interface default for the copyright is:

>>> zeit.content.image.interfaces.IImageMetadata['copyrights'].default
((u'\xa9', None),)


Make sure we don't die when there is an invalid XML snippet stored:

>>> group = zeit.cms.checkout.interfaces.ICheckoutManager(group).checkout()
>>> properties = zeit.connector.interfaces.IWebDAVProperties(group)
>>> properties[('caption', 'http://namespaces.zeit.de/CMS/image')] = u'5 < 7'
>>> group = zeit.cms.checkout.interfaces.ICheckinManager(group).checkin()
>>> ref = zope.component.getAdapter(
...     group,
...     zeit.cms.content.interfaces.IXMLReference, name='image')
>>> print lxml.etree.tostring(ref, pretty_print=True)
<image xmlns:py="http://codespeak.net/lxml/objectify/pytype"
       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       align="right"
       base-id="http://xml.zeit.de/image-group" type="jpg">
  <bu>5 &lt; 7</bu>
  <copyright py:pytype="str">Zeit online</copyright>
  <copyright py:pytype="str" link="http://xyz.de">Agentur XY</copyright>
</image>

Set the link:

>>> group = zeit.cms.checkout.interfaces.ICheckoutManager(group).checkout()
>>> zeit.content.image.interfaces.IImageMetadata(group).links_to = (
...     'http://www.asdf.com')
>>> group = zeit.cms.checkout.interfaces.ICheckinManager(group).checkin()
>>> ref = zope.component.getAdapter(
...     group,
...     zeit.cms.content.interfaces.IXMLReference, name='image')
>>> print lxml.etree.tostring(ref, pretty_print=True)
<image xmlns:py="http://codespeak.net/lxml/objectify/pytype"
       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       align="right"
       href="http://www.asdf.com"
       base-id="http://xml.zeit.de/image-group" type="jpg">
  <bu>5 &lt; 7</bu>
  <copyright py:pytype="str">Zeit online</copyright>
  <copyright py:pytype="str" link="http://xyz.de">Agentur XY</copyright>
</image>


The type attribute is rather complex.

Case 1 is simple, we've seen it above: When there is only one extension it's
used as type.

Case 2: When there is a mix of formats the type of an image whose name ends
in x140 is used:

>>> image = zeit.content.image.image.LocalImage()
>>> image.contentType = 'image/jpeg'
>>> image.open('w').write('foo')
>>> group['title-120x140.gif'] = image
>>> ref = zope.component.getAdapter(
...     group,
...     zeit.cms.content.interfaces.IXMLReference, name='image')
>>> print lxml.etree.tostring(ref, pretty_print=True)
<image
    xmlns:py="http://codespeak.net/lxml/objectify/pytype"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    align="right"
    href="http://www.asdf.com"
    base-id="http://xml.zeit.de/image-group"
    type="gif">
  <bu>5 &lt; 7</bu>
  <copyright py:pytype="str">Zeit online</copyright>
  <copyright py:pytype="str" link="http://xyz.de">Agentur XY</copyright>
</image>


Case 3: When there is a mix of formats and no image ends in x140 the "first"
one is used:

>>> del group['title-120x140.gif']
>>> image = zeit.content.image.image.LocalImage()
>>> image.contentType = 'image/jpeg'
>>> image.open('w').write('bar')
>>> group['title-120x120.gif'] = image
>>> ref = zope.component.getAdapter(
...     group,
...     zeit.cms.content.interfaces.IXMLReference, name='image')
>>> print lxml.etree.tostring(ref, pretty_print=True)
<image
    xmlns:py="http://codespeak.net/lxml/objectify/pytype"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    align="right"
    href="http://www.asdf.com"
    base-id="http://xml.zeit.de/image-group" type="jpg">
  <bu>5 &lt; 7</bu>
  <copyright py:pytype="str">Zeit online</copyright>
  <copyright py:pytype="str" link="http://xyz.de">Agentur XY</copyright>
</image>


Images whose names have no extension at all will be ignored:


>>> image = zeit.content.image.image.LocalImage()
>>> image.contentType = 'image/jpeg'
>>> image.open('w').write('blubs')
>>> group['title-120x140'] = image
>>> ref = zope.component.getAdapter(
...     group,
...     zeit.cms.content.interfaces.IXMLReference, name='image')
>>> print lxml.etree.tostring(ref, pretty_print=True)
<image
    xmlns:py="http://codespeak.net/lxml/objectify/pytype"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    align="right"
    href="http://www.asdf.com"
    base-id="http://xml.zeit.de/image-group"
    type="jpg">
  <bu>5 &lt; 7</bu>
  <copyright py:pytype="str">Zeit online</copyright>
  <copyright py:pytype="str" link="http://xyz.de">Agentur XY</copyright>
</image>
<BLANKLINE>


Cleanup
=======

>>> zope.app.component.hooks.setSite(old_site)
>>> zope.security.management.endInteraction()
