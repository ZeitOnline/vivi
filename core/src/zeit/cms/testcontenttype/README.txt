=================
Test content type
=================

The test content type is only available in tests. Its purpose is to allow
testing of other components which would have to define their own type
otherwise.

Setup ftest:

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site(locals())

Instantiate and verify the inital xml:

>>> import zeit.cms.testcontenttype.testcontenttype
>>> content = zeit.cms.testcontenttype.testcontenttype.TestContentType()
>>> import zope.component
>>> import zeit.cms.repository.interfaces
>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)
>>> content.__parent__ = repository

>>> import lxml.etree
>>> print lxml.etree.tostring(content.xml, pretty_print=True)
<testtype xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <head/>
  <body/>
</testtype>

The type provides the ITestContentType and IEditorialContent interfaces:

>>> import zope.interface.verify
>>> import zeit.cms.interfaces
>>> import zeit.cms.testcontenttype.interfaces
>>> zope.interface.verify.verifyObject(
...     zeit.cms.testcontenttype.interfaces.ITestContentType, content)
True
>>> zope.interface.verify.verifyObject(
...     zeit.cms.interfaces.IEditorialContent, content)
True


Now that was pretty boring. Add a title and year (from common metadata):

>>> content.title = u'gocept'
>>> content.year = 2008
>>> print lxml.etree.tostring(content.xml, pretty_print=True)
<testtype xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <head>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="year">2008</attribute>
  </head>
  <body>
    <title>gocept</title>
  </body>
</testtype>

Make sure we can adapt to webdav properties:

>>> import zeit.connector.interfaces
>>> properties = zeit.connector.interfaces.IWebDAVProperties(content)
>>> properties
<zeit.connector.resource.WebDAVProperties object at 0x...>
>>> import pprint
>>> pprint.pprint(dict(properties))
{('date-last-modified', u'http://namespaces.zeit.de/CMS/document'): '...',
 ('year', u'http://namespaces.zeit.de/CMS/document'): u'2008'}



Make sure we can get a browse location:

>>> import zeit.cms.browser.interfaces
>>> import zeit.cms.content.contentsource
>>> loc = zope.component.getMultiAdapter(
...     (content, zeit.cms.content.contentsource.cmsContentSource),
...     zeit.cms.browser.interfaces.IDefaultBrowsingLocation)


Browser tests
=============

>>> from z3c.etestbrowser.testing import ExtendedTestBrowser
>>> browser = ExtendedTestBrowser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')

Make sure we have a default view:

>>> browser.open('http://localhost/++skin++cms/repository/testcontent')
>>> print browser.contents
<?xml ...
    <title> testcontent – View </title>
    ... 
    <div id="edit-form" class="grouped-form">
    ...

>>> browser.getLink('View metadata').click()
>>> browser.url
'http://localhost/++skin++cms/repository/testcontent/@@view.html'


After checking out we can edit. The ressort has a "(no value)" entry which is
invalid though:

>>> browser.getLink('Checkout').click()
>>> browser.getControl('Ressort').displayValue
['(no value)']
>>> browser.getControl('Ressort').displayOptions
['(no value)', 'Deutschland', ...]
>>> browser.getControl('Apply').click()
>>> print browser.contents
<?xml ...
    <div id="messages" class="haveMessages">
      <ul>
        <li class="error">Year: Required input is missing.</li>
        <li class="error">Ressort: Required input is missing.</li>
        <li class="error">Title: Required input is missing.</li>
        <li class="error">Authors: Wrong contained type</li>
        <li class="error">Copyright (c): Required input is missing.</li>
      </ul>
      ...



>>> browser.getControl('Year').value = '2008'
>>> browser.getControl('Volume').value = '21'
>>> browser.getControl('Ressort').displayValue = ['International']
>>> browser.getControl('Title').value = 'Testing'
>>> browser.getControl(name='form.authors.0.').value = 'ich'
>>> browser.getControl('Copyright').value = 'ich'
>>> browser.getControl('Apply').click()
>>> print browser.contents
<?xml ...
    <div id="messages" class="haveMessages">
      <ul>
        <li class="message">Updated on ...</li>
      </ul>
      ...

>>> browser.getLink('Checkin').click()
