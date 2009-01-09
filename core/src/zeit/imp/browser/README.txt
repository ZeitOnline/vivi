Image Manipulation
==================

>>> import zope.testbrowser.testing
>>> browser = zope.testbrowser.testing.Browser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')


Scaled image
============
>>> browser.handleErrors = False
>>> browser.open(
...     'http://localhost/++skin++cms/repository/2006/DSC00109_2.JPG'
...     '/@@imp-scaled?width=200&height=60')
>>> print browser.headers
Status: 200 Ok
Cache-Control: public,max-age=3600
Content-Length: ...
Content-Type: image/jpeg
Last-Modified: Fri, 07 Mar 2008 12:47:16 GMT
...



Mask
====

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


Cropping
========


