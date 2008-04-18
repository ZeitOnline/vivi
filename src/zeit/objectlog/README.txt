zeit.objectlog
==============

The object log persistently stores information about import changes of an
object[#functionaltest]_.

>>> 

>>> zope.security.management.endInteraction()
>>> zope.app.component.hooks.setSite(old_site)

.. [#functionaltest] Setup functional test

    >>> import zope.app.component.hooks
    >>> old_site = zope.app.component.hooks.getSite()
    >>> zope.app.component.hooks.setSite(getRootFolder())
    
.. [#needs-interaction] 

    >>> import zope.security.management
    >>> import zope.security.testing
    >>> import zope.publisher.browser
    >>> request = zope.publisher.browser.TestRequest()
    >>> request.setPrincipal(zope.security.testing.Principal(u'hans'))
    >>> zope.security.management.newInteraction(request)
