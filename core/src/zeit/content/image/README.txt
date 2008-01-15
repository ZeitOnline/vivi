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
>>> import zeit.cms.content.interfaces
>>> ref = zeit.cms.content.interfaces.IXMLReference(group)
>>> ref
<zeit.content.image.imagegroup.XMLReference object at 0x2b34af0>
>>> print lxml.etree.tostring(ref.xml, pretty_print=True)
<image base-id="http://xml.zeit.de/image-group">
  <bu xmlns:ns0="http://www.w3.org/2001/XMLSchema-instance" ns0:nil="true"/>
  <copyright xmlns:ns1="http://www.w3.org/2001/XMLSchema-instance" ns1:nil="true"/>
</image>


Cleanup
=======

>>> zope.app.component.hooks.setSite(old_site)
