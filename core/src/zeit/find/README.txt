======
Search
======

We need to set the site since we're a functional test:

  >>> import zope.app.component.hooks
  >>> old_site = zope.app.component.hooks.getSite()
  >>> zope.app.component.hooks.setSite(getRootFolder())
