================
 Adding content
================

asdf

>>> import zope.testbrowser.testing
>>> b = zope.testbrowser.testing.Browser()
>>> b.addHeader('Authorization', 'Basic user:userpw')
>>> b.open('http://localhost/++skin++cms/@@addcentral')
>>> print b.contents
<...Type...Folder...
...Ressort...Wirtschaft...

>>> b.open('http://localhost/++skin++cms/repository/online/2007/01')
>>> print b.contents
<...Add...zeit.addcentral.panelcontent...