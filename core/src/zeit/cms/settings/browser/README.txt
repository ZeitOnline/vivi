Settings
========

The settings can be reached via a global menu item:

>>> import zope.testbrowser.testing
>>> browser = zope.testbrowser.testing.Browser()
>>> browser.addHeader('Authorization', 'Basic producer:producerpw')
>>> browser.open('http://localhost/++skin++cms/repository')
>>> browser.getLink('Global settings').click()


We can set the default year and volume:

>>> browser.getControl('Default year').value = '2006'
>>> browser.getControl('Default volume').value = '27'
>>> browser.getControl('Apply').click()
>>> print browser.contents
<?xml ...
    ...Updated on ...

