================================
Search engine optimisation (SEO)
================================

This is a small package containing views and adapters for search engingne
optimisation.

Browser Tests
=============

>>> import zeit.cms.testing
>>> browser = zeit.cms.testing.Browser(layer['wsgi_app'])
>>> browser.login('seo', 'seopw')

Open the test content and go to the SEO page:

>>> browser.open('http://localhost/++skin++cms/repository/testcontent')
>>> browser.getLink('SEO').click()
>>> print(browser.title.strip())
testcontent – View SEO data

To edit the SEO data we need to check the object out:

>>> browser.getLink('Checkout').click()
>>> print(browser.title.strip())
testcontent – Edit SEO data

Fill out the form:

>>> browser.getControl('HTML title').value = 'HTML title'
>>> browser.getControl('HTML description').value = 'HTML description'
>>> browser.getControl('Ressort').displayValue = ['Deutschland']
>>> browser.getControl('Meta robots').value = 'noindex'
>>> browser.getControl('Keyword entity type').displayValue = ['free']
>>> browser.getControl('Disable intext links').click()
>>> browser.getControl('Disable enrich').click()
>>> browser.getControl('Apply').click()

Verify the source:

>>> print(browser.getControl('HTML title').value)
HTML title
>>> print(browser.getControl('HTML description').value)
HTML description
>>> print(browser.getControl('Meta robots').value)
noindex
>>> print(browser.getControl('Keyword entity type').displayValue)
['entity-type-free']
>>> print(browser.getControl('Disable intext links').value)
on
>>> print(browser.getControl('Disable enrich').value)
on

>>> content = getRootFolder()['workingcopy']['zope.seo']['testcontent']
>>> import zeit.retresco.interfaces
>>> zeit.retresco.interfaces.ISkipEnrich.providedBy(content)
True


Go back to the SEO tab and check in. We're still at the SEO view then:

>>> browser.getLink('SEO').click()
>>> browser.getLink('Checkin').click()
>>> print(browser.title.strip())
testcontent – View SEO data


Python level tests
==================

There is an adapter from ICMSContent to ISEO. The SEO information is stored in
WebDAV properties which each and every content type has. The views are
registered on ICommonMetadata because in reality it doesn't make sense to add
SEO information for other types (such as images).

Create an unknown resource and adapt it to ISEO:

>>> import zeit.seo.interfaces
>>> import zeit.cms.repository.unknown
>>> content = zeit.cms.repository.unknown.UnknownResource('')
>>> seo = zeit.seo.interfaces.ISEO(content)
>>> seo
<zeit.seo.seo.SEO object at 0x...>


Let's set the title and description:

>>> seo.html_title = 'Special title'
>>> seo.html_description = 'Very special description'

The properties are now set at `content`:

>>> properties = zeit.connector.interfaces.IWebDAVProperties(content)
>>> properties[('html-meta-title', 'http://namespaces.zeit.de/CMS/document')]
'Special title'
>>> properties[('html-meta-description',
...             'http://namespaces.zeit.de/CMS/document')]
'Very special description'
