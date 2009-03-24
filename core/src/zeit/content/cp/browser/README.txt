==========
Centerpage
==========

>>> from zope.testbrowser.testing import Browser
>>> b = Browser()
>>> b.addHeader('Authorization', 'Basic user:userpw')
>>> b.open('http://localhost/++skin++cms')
