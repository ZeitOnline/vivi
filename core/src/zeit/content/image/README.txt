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
</image>


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
((u'ZEIT ONLINE', 'http://www.zeit.de/'),)


Make sure we don't die when there is an invalid XML snippet stored:

>>> import zeit.connector.interfaces
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

Case 2: When there is a mix of formats the type an object which ends in x140 is 
used:

>>> import zeit.content.image.image
>>> group['title-120x140.gif'] = zeit.content.image.image.Image()
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
>>> group['title-120x120.gif'] = zeit.content.image.image.Image()
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


Cleanup
=======

>>> zope.app.component.hooks.setSite(old_site)
>>> zope.security.management.endInteraction()
