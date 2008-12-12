Image Manipulation
==================

>>> import zope.testbrowser.testing
>>> browser = zope.testbrowser.testing.Browser()

Mask
====

The mask is loaded from the site with the image size and mask size parameters:

>>> import urllib
>>> query = urllib.urlencode({
...     'image_width:int': '100',
...     'image_height:int': '200',
...     'mask_width:int': '20',
...     'mask_height:int': '10'})
>>> browser.open('http://localhost/++skin++cms/@@imp-cut-mask?' + query)
>>> print browser.headers
Status: 200 Ok
Cache-Control: public;max-age=86400
Content-Length: ...
Content-Type: image/png
...
>>> browser.contents[:10]
'\x89PNG\r\n\x1a\n\x00\x00'
