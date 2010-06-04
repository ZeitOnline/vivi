=====================
Displaying references
=====================

[#prepare-testcontent]_

>>> import zope.testbrowser.testing
>>> browser = zope.testbrowser.testing.Browser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')
>>> browser.open(
...     'http://localhost/++skin++cms/repository/testcontent')

>>> import zeit.cms.testcontenttype.testcontenttype
>>> import zeit.cms.repository.interfaces
>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()
>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)
>>> content = zeit.cms.testcontenttype.testcontenttype.TestContentType()
>>> content.title = 'Some Article'
>>> repository['test2'] = content

>>> browser.getLink('Checkout').click()
>>> browser.getLink('Edit assets').click()
>>> browser.getControl('Add Related content').click()
>>> browser.getControl(name='form.related.0.').value = \
...     'http://xml.zeit.de/test2'
>>> browser.getControl('Apply').click()
>>> browser.getLink('Checkin').click()

>>> browser.handleErrors = False
>>> browser.open(
...     'http://localhost/++skin++cms/repository/test2')
>>> browser.getLink('References').click()
>>> print browser.contents
<...http://xml.zeit.de/testcontent...

Clean up:

>>> zope.interface.classImplementsOnly(
...     zeit.cms.testcontenttype.testcontenttype.TestContentType,
...     *old_implements)


.. [#prepare-testcontent] Let the test content provide IAssetViews:

    >>> import zope.interface
    >>> import zeit.cms.content.browser.interfaces
    >>> import zeit.cms.testcontenttype.testcontenttype
    >>> old_implements = list(zope.interface.implementedBy(
    ...     zeit.cms.testcontenttype.testcontenttype.TestContentType))
    >>> zope.interface.classImplements(
    ...     zeit.cms.testcontenttype.testcontenttype.TestContentType,
    ...     zeit.cms.content.browser.interfaces.IAssetViews)
