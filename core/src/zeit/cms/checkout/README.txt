================
Checkout Manager
================

The checkout manager is an adapter to ICMSContent managing the checkin/checkout
process.

We need to set the site since we're a functional test:

>>> import zope.app.component.hooks
>>> old_site = zope.app.component.hooks.getSite()
>>> zope.app.component.hooks.setSite(getRootFolder())

We also need an interaction as checkout manager needs to get the principal:

>>> import zope.security.testing
>>> principal = zope.security.testing.Principal(u'zope.user')
>>> participation = zope.security.testing.Participation(principal)
>>> import zope.security.management
>>> zope.security.management.newInteraction(participation)


We also subscribe a testing handler to the CheckoutEvent:

>>> def checkoutEvent(context, event):
...     print 'Event:', event
...     print '    Principal:', principal.id
...     print '    Content:', context
...
>>> import zope.component
>>> from zeit.cms.interfaces import ICMSContent
>>> from zeit.cms.checkout.interfaces import ICheckinCheckoutEvent
>>> site_manager = zope.component.getSiteManager()
>>> site_manager.registerHandler(
...     checkoutEvent,
...     (ICMSContent, ICheckinCheckoutEvent))


Checking out
============

After checking out a copy of the managed object resides in the user's working
copy. Get a content object first:

>>> from zeit.cms.repository.interfaces import IRepository
>>> repository = zope.component.getUtility(IRepository)
>>> collection = repository['online']['2007']['01']
>>> content = list(collection.values())[0]
>>> ICMSContent.providedBy(content)
True

For adapting the content to to ICheckoutManager we also need a principaal:

>>> from zope.app.security.interfaces import IAuthentication
>>> from zeit.cms.checkout.interfaces import (
...     ICheckoutManager, ICheckinManager)

>>> manager = ICheckoutManager(content)
>>> manager
<zeit.cms.checkout.manager.CheckoutManager object at 0x...>


The checkout manager can tell if the object can actually be checked out.
Objects from the repository usually can be checked out. They might be locked
which prevents checkout though:

>>> manager.canCheckout
True


When we check out the document, we will find a copy in the working copy:

>>> from zeit.cms.workingcopy.interfaces import IWorkingcopy
>>> workingcopy = IWorkingcopy(principal)
>>> list(workingcopy.keys())
[]
>>> manager.checkout()
Event: <zeit.cms.checkout.interfaces.CheckoutEvent object at 0x...>
    Principal: zope.user
    Content: <zeit.cms...>
>>> workingcopy = IWorkingcopy(principal)
>>> list(workingcopy.keys())
[u'4schanzentournee-abgesang']
>>> list(workingcopy.values())
[<zeit.cms.repository.unknown.UnknownResource object at 0x...]


After checking out the resource is locked in the WebDAV. This means other users
cannot check it out. We can:

>>> manager.canCheckout
True 

Other users cannot check it out. Login another user called `bob`:

>>> zope.security.management.endInteraction()
>>> import zope.security.testing
>>> principal = zope.security.testing.Principal('bob')
>>> participation = zope.security.testing.Participation(principal)
>>> import zope.security.management
>>> zope.security.management.newInteraction(participation)

Bob cannot check out:

>>> manager.canCheckout
False

Let's log back in as the `zope.user`:

>>> zope.security.management.endInteraction()
>>> import zope.security.testing
>>> principal = zope.security.testing.Principal('zope.user')
>>> participation = zope.security.testing.Participation(principal)
>>> import zope.security.management
>>> zope.security.management.newInteraction(participation)


Checking in
===========

Checking in means removing an object from the working copy and "putting it
back" into the repository. 

Get the object we cecked out above from the working copy and modify it:

>>> checked_out = workingcopy['4schanzentournee-abgesang']
>>> checked_out.data = u'Lorem ipsum.'


So far nothing in the repository has changed:

>>> content = repository.getContent(checked_out.uniqueId)
>>> content.data
u'<?xml version="1.0" ...'

But now we check in:

>>> manager = ICheckinManager(checked_out)
>>> manager.canCheckin
True
>>> manager.checkin()
Event: <zeit.cms.checkout.interfaces.CheckinEvent object at 0x...>
     Principal: zope.user
     Content: <zeit.cms...>

Now the object is no longer in the working copy:

>>> list(workingcopy.keys())
[]

When we get the object from the repository, it now contains `Lorem ipsum.` and
we can check it out again:

>>> content = repository.getContent(checked_out.uniqueId)
>>> content.data
u'Lorem ipsum.'
>>> manager = ICheckoutManager(content)
>>> manager.canCheckout
True
>>> manager = ICheckinManager(content)
>>> manager.canCheckin
False 
>>> lockable = zope.app.locking.interfaces.ILockable(content)
>>> lockable.locked()
False



Deleting in the Working Copy
============================

When the user checks out a dokument and just deletes it from his workingcopy
the object is no longer locked in the dav:

>>> manager = ICheckoutManager(content)
>>> lockable.locked()
False
>>> checked_out = manager.checkout()
Event: <zeit.cms.checkout.interfaces.CheckoutEvent object at 0x...>
    Principal: zope.user
    Content: <zeit.cms.repository.unknown.UnknownResource object at 0x...>
>>> lockable.locked()
True 
>>> working_copy = checked_out.__parent__
>>> del working_copy[checked_out.__name__]
>>> lockable.locked()
False



Cleanup
=======

After the test we restore the old site:

>>> zope.security.management.endInteraction()
>>> site_manager.unregisterHandler(
...     checkoutEvent,
...     (ICMSContent, ICheckinCheckoutEvent))
True
>>> zope.app.component.hooks.setSite(old_site)
