================================
Search engine optimisation (SEO)
================================

This is a small package containing views and adapters for search engingne
optimisation.

Browser Tests
=============

>>> from z3c.etestbrowser.testing import ExtendedTestBrowser
>>> browser = ExtendedTestBrowser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')

Open the test content and go to the SEO page:

>>> browser.open('http://localhost/++skin++cms/repository/testcontent')

#>>> browser.getLink('SEO').click()
#>>> print browser.contents


Python level tests
==================

There is an adapter from ICMSContent to ISEO. The SEO information is stored in
WebDAV properties which each and every content type has. The views are
registered on ICommonMetadata because in reality it doesn't make sense to add
SEO information for other types (such as images).

Create an unknown resource and adapt it to ISEO:

>>> import zeit.seo.interfaces
>>> import zeit.cms.repository.unknown
>>> content = zeit.cms.repository.unknown.UnknownResource(u'')
>>> seo = zeit.seo.interfaces.ISEO(content)
>>> seo
<zeit.seo.seo.SEO object at 0x...>


Let's set the title and description:

>>> seo.html_title = u'Special title'
>>> seo.html_description = u'Very special description'

The properties are now set at `content`:

>>> properties = zeit.connector.interfaces.IWebDAVProperties(content)
>>> properties[(u'html-meta-title', u'http://namespaces.zeit.de/CMS/document')]
u'Special title'
>>> properties[(u'html-meta-description',
...             u'http://namespaces.zeit.de/CMS/document')]
u'Very special description'
