=================
Test content type
=================

The test content type is only available in tests. Its purpose is to allow
testing of other components which would have to define their own type
otherwise.

Setup ftest:

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()

Instantiate and verify the inital xml:

>>> import zeit.cms.testcontenttype.testcontenttype
>>> content = zeit.cms.testcontenttype.testcontenttype.ExampleContentType()
>>> import zope.component
>>> import zeit.cms.repository.interfaces
>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)
>>> content.__parent__ = repository

>>> print(zeit.cms.testing.xmltotext(content.xml))
<testtype>
  <head/>
  <body/>
</testtype>

The type provides the IExampleContentType and IEditorialContent interfaces:

>>> import zope.interface.verify
>>> import zeit.cms.interfaces
>>> import zeit.cms.testcontenttype.interfaces
>>> zope.interface.verify.verifyObject(
...     zeit.cms.testcontenttype.interfaces.IExampleContentType, content)
True
>>> zope.interface.verify.verifyObject(
...     zeit.cms.interfaces.IEditorialContent, content)
True


Now that was pretty boring. Add a title and year (from common metadata):

>>> content.title = 'gocept'
>>> content.year = 2008
>>> print(zeit.cms.testing.xmltotext(content.xml))
<testtype...
  <body>
    <title>gocept</title>
  </body>
</testtype>

Make sure we can adapt to webdav properties:

>>> import zeit.connector.interfaces
>>> properties = zeit.connector.interfaces.IWebDAVProperties(content)
>>> properties
<zeit.connector.resource.WebDAVProperties object at 0x...>
>>> properties[('year', 'http://namespaces.zeit.de/CMS/document')]
'2008'



Make sure we can get a browse location:

>>> import zeit.cms.browser.interfaces
>>> import zeit.cms.content.contentsource
>>> loc = zope.component.getMultiAdapter(
...     (content, zeit.cms.content.contentsource.cmsContentSource),
...     zeit.cms.browser.interfaces.IDefaultBrowsingLocation)


Browser tests
=============

>>> from zeit.cms.testing import Browser
>>> browser = Browser(layer['wsgi_app'])
>>> browser.login('user', 'userpw')

Make sure we have a default view:

>>> browser.open('http://localhost/++skin++cms/repository/testcontent')
>>> print(browser.contents)
<?xml ...
    <title> testcontent – View </title>
    ...
    <div id="edit-form" class="grouped-form">
    ...

>>> browser.getLink('View metadata').click()
>>> browser.url
'http://localhost/++skin++cms/repository/testcontent/@@view.html'


After checking out we can edit. The ressort has a "(nothing selected)" entry
which is invalid though:

>>> browser.getLink('Checkout').click()
>>> browser.getControl('Ressort').displayValue
['(nothing selected)']
>>> browser.getControl('Ressort').displayOptions
['(nothing selected)', 'Deutschland', ...]
>>> browser.getControl('Apply').click()
>>> print(browser.contents)
<?xml ...
    <div id="messages" class="haveMessages">
      <ul>
        <li class="error">Ressort: Required input is missing.</li>
        <li class="error">Title: Required input is missing.</li>
        <li class="error">Authors (freetext): Wrong contained type</li>
      </ul>
      ...



>>> browser.getControl('Year').value = '2008'
>>> browser.getControl('Volume').value = '21'
>>> browser.getControl('Ressort').displayValue = ['International']
>>> browser.getControl('Title').value = 'Testing'
>>> browser.getControl(name='form.authors.0.').value = 'ich'
>>> browser.getControl('Copyright').value = 'ich'
>>> browser.getControl('Apply').click()
>>> print(browser.contents)
<?xml ...
    <div id="messages" class="haveMessages">
      <ul>
        <li class="message">Updated on ...</li>
      </ul>
      ...

>>> browser.getLink('Checkin').click()
