Image Manipulation
==================

[#setup]_

Scaled image
++++++++++++

>>> browser.open(
...     'http://localhost/++skin++cms/repository/group'
...     '/@@imp-scaled?width=200&height=60')
>>> print browser.headers
Status: 200 Ok
Cache-Control: public,max-age=3600
Content-Length: ...
Content-Type: image/jpeg
...



Mask
++++

The mask is loaded from the site with the image size and mask size parameters:

>>> import urllib
>>> query = urllib.urlencode({
...     'image_width:int': '100',
...     'image_height:int': '200',
...     'mask_width:int': '20',
...     'mask_height:int': '10',
...     'border': ''})
>>> browser.open('http://localhost/++skin++cms/@@imp-cut-mask?' + query)
>>> print browser.headers
Status: 200 Ok
Cache-Control: public,max-age=86400
Content-Length: ...
Content-Type: image/png
...
>>> browser.contents[:10]
'\x89PNG\r\n\x1a\n\x00\x00'

The border can be coloured:

>>> query = urllib.urlencode({
...     'image_width:int': '100',
...     'image_height:int': '200',
...     'mask_width:int': '20',
...     'mask_height:int': '10',
...     'border': '#fde32b'})
>>> browser.open('http://localhost/++skin++cms/@@imp-cut-mask?' + query)
>>> print browser.headers
Status: 200 Ok
Cache-Control: public,max-age=86400
Content-Length: ...
Content-Type: image/png
...

If the colour doesn't parse there will not be a border:

>>> query = urllib.urlencode({
...     'image_width:int': '100',
...     'image_height:int': '200',
...     'mask_width:int': '20',
...     'mask_height:int': '10',
...     'border': '#xzy'})
>>> browser.open('http://localhost/++skin++cms/@@imp-cut-mask?' + query)
>>> print browser.headers
Status: 200 Ok
Cache-Control: public,max-age=86400
Content-Length: ...
Content-Type: image/png
...


Image manipulation view
+++++++++++++++++++++++

The image manipulation view is on an imagegroup containing a master image:

>>> browser.open('http://localhost/++skin++cms/repository/group')
>>> browser.getLink('Transform').click()
>>> print browser.contents
<?xml ...
  <div id="imp-metadata">
    <div id="imp-width">2048</div>
    <div id="imp-height">1536</div>
    <div id="imp-image-url">http://localhost/++skin++cms/repository/group/master-image.jpg</div>
  </div>
  ...


When there is no master image we get an error page telling us what to do:


>>> browser.open('http://localhost/++skin++cms/repository/image-group')
>>> browser.getLink('Transform').click()
>>> print browser.contents
<!DOCTYPE...
     ...There is no master image...
     

It is possible to check out the group from here directly:

>>> browser.getLink('Checkout').click()
>>> browser.getControl('Master image').displayValue
['(no value)']


.. [#setup]

    >>> import zope.testbrowser.testing
    >>> browser = zope.testbrowser.testing.Browser()
    >>> browser.addHeader('Authorization', 'Basic user:userpw')
    >>> import zope.app.component.hooks
    >>> old_site = zope.app.component.hooks.getSite()
    >>> zope.app.component.hooks.setSite(getRootFolder())
    >>> import zeit.content.image.testing
    >>> grp = zeit.content.image.testing.create_image_group_with_master_image()
    >>> grp = zeit.content.image.testing.create_image_group()
    >>> zope.app.component.hooks.setSite(old_site)
