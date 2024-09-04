================
Checkout Manager
================

The checkout manager is an adapter to ICMSContent managing the checkin/checkout
process.

We need an interaction as checkout manager needs to get the principal:

>>> import zeit.cms.testing
>>> principal = zeit.cms.testing.create_interaction()
>>> zeit.cms.testing.set_site()

We also subscribe a testing handler to the CheckoutEvent:

>>> def checkoutEvent(context, event):
...     print('Event: %s' % event)
...     print('    Principal: %s' % event.principal.id)
...     print('    Content: %s' % context)
...     print('    Workingcopy: %s' % event.workingcopy)
...
>>> import zope.component
>>> from zeit.cms.interfaces import ICMSContent
>>> from zeit.cms.checkout.interfaces import ICheckinCheckoutEvent
>>> site_manager = zope.component.getGlobalSiteManager()
>>> site_manager.registerHandler(
...     checkoutEvent,
...     (ICMSContent, ICheckinCheckoutEvent))


Checking out
============

After checking out a copy of the managed object resides in the user's working
copy. Get a content object first:

>>> import zeit.cms.repository.interfaces
>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)
>>> collection = repository['online']['2007']['01']
>>> content = list(collection.values())[0]
>>> ICMSContent.providedBy(content)
True

For adapting the content to to ICheckoutManager we also need a principal:

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

Note that we cannot checkout normal collections:

>>> ICheckoutManager(collection).canCheckout
False


When we check out the document, we will find a copy in the working copy:

>>> from zeit.cms.workingcopy.interfaces import IWorkingcopy
>>> workingcopy = IWorkingcopy(principal)
>>> list(workingcopy.keys())
[]
>>> manager.checkout()
Event: <zeit.cms.checkout.interfaces.BeforeCheckoutEvent object at 0x...>
    Principal: zope.user
    Content: <zeit.cms...>
    Workingcopy: <zeit.cms.workingcopy.workingcopy.Workingcopy object at 0x...>
Event: <zeit.cms.checkout.interfaces.AfterCheckoutEvent object at 0x...>
    Principal: zope.user
    Content: <zeit.cms...>
    Workingcopy: <zeit.cms.workingcopy.workingcopy.Workingcopy object at 0x...>
>>> workingcopy = IWorkingcopy(principal)
>>> list(workingcopy.keys())
['4schanzentournee-abgesang']
>>> list(workingcopy.values())
[<zeit.cms.repository.unknown.PersistentUnknownResource...4schanzentournee-abgesang>]

The resource is locked in DAV for about an hour:

>>> lockable = zope.app.locking.interfaces.ILockable(content)
>>> lockable.locked()
True
>>> int(round(lockable.getLockInfo().timeout))
3600

After checking out the resource is locked in the WebDAV. This means other users
cannot check it out. Login another user called `bob`:

>>> zope.security.management.endInteraction()
>>> principal = zeit.cms.testing.create_interaction('bob')

Bob cannot check out:

>>> manager = ICheckoutManager(content)
>>> manager.canCheckout
False
>>> manager.checkout()
Traceback (most recent call last):
    ...
CheckinCheckoutError: The content object is locked by ${name}.



Let's log back in as the `zope.user`.

>>> zope.security.management.endInteraction()
>>> principal = zeit.cms.testing.create_interaction('zope.user')

We also cannot check it out because checking out is only possible once:

>>> manager = ICheckoutManager(content)
>>> manager.canCheckout
False


Checking in
===========

Checking in means removing an object from the working copy and "putting it
back" into the repository.

Get the object we cecked out above from the working copy and modify it:

>>> checked_out = workingcopy['4schanzentournee-abgesang']
>>> checked_out.data = 'Lorem ipsum.'


So far nothing in the repository has changed:

>>> content = repository.getContent(checked_out.uniqueId)
>>> content.data
'<?xml version="1.0" ...'

But now we check in:

>>> manager = ICheckinManager(checked_out)
>>> manager.canCheckin
Event: <zeit.cms.checkout.interfaces.ValidateCheckinEvent...
True
>>> checked_in = manager.checkin()
Event: <zeit.cms.checkout.interfaces.ValidateCheckinEvent...
Event: <zeit.cms.checkout.interfaces.BeforeCheckinEvent object at 0x...>
     Principal: zope.user
     Content: <zeit.cms...>
     Workingcopy: <zeit.cms.workingcopy.workingcopy.Workingcopy object at 0x...>
Event: <zeit.cms.checkout.interfaces.AfterCheckinEvent object at 0x...>
     Principal: zope.user
     Content: <zeit.cms...>
     Workingcopy: <zeit.cms.workingcopy.workingcopy.Workingcopy object at 0x...>

`checked_in` is the object in the repository:

>>> zeit.cms.repository.interfaces.IRepositoryContent.providedBy(checked_in)
True

Now the object is no longer in the working copy:

>>> list(workingcopy.keys())
[]

When we get the object from the repository, it now contains `Lorem ipsum.` and
we can check it out again:

>>> content = repository.getContent(checked_out.uniqueId)
>>> content.data
'Lorem ipsum.'
>>> manager = ICheckoutManager(content)
>>> manager.canCheckout
True
>>> manager = ICheckinManager(content)
>>> manager.canCheckin
False
>>> import zope.app.locking.interfaces
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
Event: <zeit.cms.checkout.interfaces.BeforeCheckoutEvent object at 0x...>
    Principal: zope.user
    Content: <zeit.cms.repository.unknown.PersistentUnknownResource...>
    Workingcopy: <zeit.cms.workingcopy.workingcopy.Workingcopy object at 0x...>
Event: <zeit.cms.checkout.interfaces.AfterCheckoutEvent object at 0x...>
    Principal: zope.user
    Content: <zeit.cms.repository.unknown.PersistentUnknownResource...>
    Workingcopy: <zeit.cms.workingcopy.workingcopy.Workingcopy object at 0x...>
>>> lockable.locked()
True
>>> manager = ICheckinManager(checked_out)
>>> manager.delete()
Event: <zeit.cms.checkout.interfaces.BeforeDeleteEvent object at 0x...>
    Principal: zope.user
    Content: <zeit.cms.repository.unknown.PersistentUnknownResource...>
    Workingcopy: <zeit.cms.workingcopy.workingcopy.Workingcopy object at 0x...>
Event: <zeit.cms.checkout.interfaces.AfterDeleteEvent object at 0x...>
    Principal: zope.user
    Content: <zeit.cms.repository.unknown.PersistentUnknownResource...>
    Workingcopy: <zeit.cms.workingcopy.workingcopy.Workingcopy object at 0x...>
>>> lockable.locked()
False


Temporary checkouts
===================

There are quite some system events which do checkouts. Those should not
interfere with the user. The system usually checks out content as "temporary".

>>> manager = ICheckoutManager(content)
>>> checked_out = manager.checkout(temporary=True)
Event: <zeit.cms.checkout.interfaces.BeforeCheckoutEvent object at 0x...>
    Principal: zope.user
    Content: <zeit.cms.repository.unknown.PersistentUnknownResource...>
    Workingcopy: <zeit.cms.workingcopy.workingcopy.Workingcopy object at 0x...>
Event: <zeit.cms.checkout.interfaces.AfterCheckoutEvent object at 0x...>
    Principal: zope.user
    Content: <zeit.cms.repository.unknown.PersistentUnknownResource...>
    Workingcopy: <zeit.cms.workingcopy.workingcopy.Workingcopy object at 0x...>

The workingcopy is still empty:

>>> list(workingcopy.keys())
[]

The checked out content is stored in a temporary workingcopy:

>>> checked_out.__parent__
<zeit.cms.workingcopy.workingcopy.Workingcopy object at 0x...>
>>> checked_out.__parent__.__parent__ is None
True
>>> list(checked_out.__parent__.keys())
['4schanzentournee-abgesang']


The lock timeout is small for temporary checkouts (around 30 seconds):

>>> lockable = zope.app.locking.interfaces.ILockable(content)
>>> lockable.locked()
True
>>> int(round(lockable.getLockInfo().timeout))
30

We can also check in the temporary checkout:

>>> manager = ICheckinManager(checked_out)
>>> manager.canCheckin
True
>>> manager.checkin()
Event: <zeit.cms.checkout.interfaces.BeforeCheckinEvent object at 0x...>
    Principal: zope.user
    Content: <zeit.cms.repository.unknown.PersistentUnknownResource...>
    Workingcopy: <zeit.cms.workingcopy.workingcopy.Workingcopy object at 0x...>
Event: <zeit.cms.checkout.interfaces.AfterCheckinEvent object at 0x...>
    Principal: zope.user
    Content: <zeit.cms.repository.unknown.PersistentUnknownResource...>
    Workingcopy: <zeit.cms.workingcopy.workingcopy.Workingcopy object at 0x...>
<zeit.cms.repository.unknown.PersistentUnknownResource...>


Locking race condition
======================

There is a race condition in regard to locking: When the object is locked
by another thread before the checkout has locked, a CheckinCheckoutError is
raised.

We provide a special LockStorage to simulate the behaviour:

>>> import zeit.cms.locking.locking
>>> class LockStorage(zeit.cms.locking.locking.LockStorage):
...     def setLock(self, object, lock):
...         raise zope.app.locking.interfaces.LockingError(object.uniqueId)
...
>>> lock_storage = LockStorage()
>>> zope.component.getGlobalSiteManager().registerUtility(
...     lock_storage, zope.app.locking.interfaces.ILockStorage)

Now try to checkout:

>>> manager = ICheckoutManager(content)
>>> manager.canCheckout
True
>>> manager.checkout()
Traceback (most recent call last):
    ...
CheckinCheckoutError

Remove the utility registration:

>>> zope.component.getGlobalSiteManager().unregisterUtility(
...     lock_storage, zope.app.locking.interfaces.ILockStorage)
True

Remove the event printer:

>>> site_manager.unregisterHandler(
...     checkoutEvent,
...     (ICMSContent, ICheckinCheckoutEvent))
True


Conflicts
=========

It is possible to override conflicts when checking in.

>>> manager = ICheckoutManager(content)
>>> checked_out = manager.checkout()

Provoke a conflict:

>>> import zeit.cms.testcontenttype.testcontenttype
>>> content.__parent__[content.__name__] = (
...     zeit.cms.testcontenttype.testcontenttype.ExampleContentType())

Checking in is not possible just like that:

>>> ICheckinManager(checked_out).checkin()
Traceback (most recent call last):
    ...
ConflictError

Checking in is possible with ignored conflicts:

>>> ICheckinManager(checked_out).checkin(ignore_conflicts=True)
<zeit.cms.repository.unknown.PersistentUnknownResource...4schanzentournee-abgesang>
