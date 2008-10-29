Settings
========

The settings can be reached via a global menu item:

>>> import zope.testbrowser.testing
>>> browser = zope.testbrowser.testing.Browser()
>>> browser.addHeader('Authorization', 'Basic producer:producerpw')
>>> browser.open('http://localhost/++skin++cms/repository')
>>> browser.handleErrors = False
>>> browser.getLink('Global settings').click()


We can set the default year and volume:

>>> browser.getControl('Default year').value = '2006'
>>> browser.getControl('Default volume').value = '27'
>>> browser.getControl('Apply').click()
>>> print browser.contents
<?xml ...
    ...Updated on ...



There is a view which puts out the settings as xml. It is reachable
anonymously:

>>> browser = zope.testbrowser.testing.Browser()
>>> browser.open('http://localhost/++skin++cms/@@global-settings.xml')
>>> print browser.contents,
<?xml version="1.0"?>
<global-settings>
  <year>2006</year>
  <volume>27</volume>
</global-settings>

>>> print browser.headers
Status: 200 Ok
...
Content-Type: text/xml;charset=utf-8
...
