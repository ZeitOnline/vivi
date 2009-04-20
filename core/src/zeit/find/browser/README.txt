=========
Search UI
=========

For UI-Tests we need a Testbrowser:

>>> from zope.testbrowser.testing import Browser
>>> browser = Browser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')



>>> browser.open('http://localhost:8080/++skin++cms/find')

The content-type of a find-result is everytime `text/json`:

>>> browser.headers['Content-Type']
'text/json'

If the find-query is empty, we get an empty result as well:

>>> print browser.contents
{}

>>> browser.open('http://localhost:8080/++skin++cms/testfind')
>>> print browser.contents
