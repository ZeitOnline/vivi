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

Set the copyright:

>>> group = zeit.cms.checkout.interfaces.ICheckoutManager(group).checkout()
>>> zeit.content.image.interfaces.IImageMetadata(group).copyrights = (
...     ('Zeit online', None),
...     ('Agentur XY', 'http://xyz.de'))
>>> group = zeit.cms.checkout.interfaces.ICheckinManager(group).checkin()
>>> ref = zope.component.getAdapter(
...     group,
...     zeit.cms.content.interfaces.IXMLReference, name='image')
>>> print lxml.etree.tostring(ref, pretty_print=True)
<image xmlns:py="http://codespeak.net/lxml/objectify/pytype"
       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       base-id="http://xml.zeit.de/image-group" type="jpg">
  <bu xsi:nil="true"/>
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
       href="http://www.asdf.com"
       base-id="http://xml.zeit.de/image-group" type="jpg">
  <bu xsi:nil="true"/>
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
    href="http://www.asdf.com"
    base-id="http://xml.zeit.de/image-group"
    type="gif">
  <bu xsi:nil="true"/>
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
    href="http://www.asdf.com"
    base-id="http://xml.zeit.de/image-group" type="jpg">
  <bu xsi:nil="true"/>
  <copyright py:pytype="str">Zeit online</copyright>
  <copyright py:pytype="str" link="http://xyz.de">Agentur XY</copyright>
</image>


Cleanup
=======

>>> zope.app.component.hooks.setSite(old_site)
>>> zope.security.management.endInteraction()
