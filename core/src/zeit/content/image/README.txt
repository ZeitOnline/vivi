=======================
Images and image groups
=======================

Images contain the image data and some metadata. An image group contains
several images.

Setup functional test:

>>> import zope.app.component.hooks
>>> old_site = zope.app.component.hooks.getSite()
>>> zope.app.component.hooks.setSite(getRootFolder())

Image group
===========

XML reference
+++++++++++++

Create an image group first:

>>> import zeit.content.image.test
>>> group = zeit.content.image.test.create_image_group()


Reference the image via XML:

>>> import lxml.etree
>>> import zope.component
>>> import zeit.cms.content.interfaces
>>> ref = zope.component.getAdapter(
...     group,
...     zeit.cms.content.interfaces.IXMLReference, name='image')
>>> print lxml.etree.tostring(ref, pretty_print=True)
<image xmlns:py="http://codespeak.net/lxml/objectify/pytype"
       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       base-id="http://xml.zeit.de/image-group">
  <bu xsi:nil="true"/>
</image>

Set the copyright:

>>> zeit.content.image.interfaces.IImageMetadata(group).copyrights = (
...     ('Zeit online', None),
...     ('Agentur XY', 'http://xyz.de'))
>>> ref = zope.component.getAdapter(
...     group,
...     zeit.cms.content.interfaces.IXMLReference, name='image')
>>> print lxml.etree.tostring(ref, pretty_print=True)
<image xmlns:py="http://codespeak.net/lxml/objectify/pytype"
       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       base-id="http://xml.zeit.de/image-group">
  <bu xsi:nil="true"/>
  <copyright py:pytype="str">Zeit online</copyright>
  <copyright py:pytype="str" link="http://xyz.de">Agentur XY</copyright>
</image>


Set the link:

>>> zeit.content.image.interfaces.IImageMetadata(group).links_to = (
...     'http://www.asdf.com')
>>> ref = zope.component.getAdapter(
...     group,
...     zeit.cms.content.interfaces.IXMLReference, name='image')
>>> print lxml.etree.tostring(ref, pretty_print=True)
<image xmlns:py="http://codespeak.net/lxml/objectify/pytype"
       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       href="http://www.asdf.com"
       base-id="http://xml.zeit.de/image-group">
  <bu xsi:nil="true"/>
  <copyright py:pytype="str">Zeit online</copyright>
  <copyright py:pytype="str" link="http://xyz.de">Agentur XY</copyright>
</image>

Cleanup
=======

>>> zope.app.component.hooks.setSite(old_site)
