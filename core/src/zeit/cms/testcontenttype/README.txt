=================
Test content type
=================

The test content type is only available in tests. Its purpose is to allow
testing of other components which would have to define their own type
otherwise.

Instanciate and verify the inital xml:

>>> import zeit.cms.testcontenttype.testcontenttype
>>> content = zeit.cms.testcontenttype.testcontenttype.TestContentType()

>>> import lxml.etree
>>> print lxml.etree.tostring(content.xml, pretty_print=True)
<testtype xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <head/>
  <body/>
</testtype>

Now that was pretty boring. Add a title and year (from common metadata):

>>> content.title = u'gocept'
>>> content.year = 2008
>>> print lxml.etree.tostring(content.xml, pretty_print=True)
<testtype xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <head/>
  <body>
    <title>gocept</title>
  </body>
</testtype>


Browser tests
=============

>>> from z3c.etestbrowser.testing import ExtendedTestBrowser
>>> browser = ExtendedTestBrowser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')

Make sure we have a default view:

>>> browser.open('http://localhost/++skin++cms/repository/testcontent')
>>> print browser.contents
<?xml ...
    <title> View </title>
    ... 
    <div id="edit-form" class="grouped-form">
    ...

>>> browser.getLink('View metadata').click()
>>> browser.url
'http://localhost/++skin++cms/repository/testcontent/@@view.html'
