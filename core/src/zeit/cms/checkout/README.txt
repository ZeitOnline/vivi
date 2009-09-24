================
Checkout Manager
================

The checkout manager is an adapter to ICMSContent managing the checkin/checkout
process[#functional]_.

We need an interaction as checkout manager needs to get the principal:

>>> import zeit.cms.testing
>>> principal = zeit.cms.testing.create_interaction()

We also subscribe a testing handler to the CheckoutEvent:

>>> def checkoutEvent(context, event):
...     print 'Event:', event
...     print '    Principal:', event.principal.id
...     print '    Content:', context
...     print '    Workingcopy:', event.workingcopy
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
[u'4schanzentournee-abgesang']
>>> list(workingcopy.values())
[<zeit.cms.repository.unknown.PersistentUnknownResource object at 0x...]

The resource is locked in DAV for about an hour:

>>> lockable = zope.app.locking.interfaces.ILockable(content)
>>> lockable.locked()
True
>>> round(lockable.getLockInfo().timeout)
3600.0

After checking out the resource is locked in the WebDAV. This means other users
cannot check it out. Login another user called `bob`:

>>> zope.security.management.endInteraction()
>>> principal = zeit.cms.testing.create_interaction(u'bob')

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
>>> principal = zeit.cms.testing.create_interaction(u'zope.user')

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
>>> checked_out.data = u'Lorem ipsum.'


So far nothing in the repository has changed:

>>> content = repository.getContent(checked_out.uniqueId)
>>> content.data
u'<?xml version="1.0" ...'

But now we check in:

>>> manager = ICheckinManager(checked_out)
>>> manager.canCheckin
True
>>> checked_in = manager.checkin()
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
u'Lorem ipsum.'
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
    Content: <zeit.cms.repository.unknown.PersistentUnknownResource object at 0x...>
    Workingcopy: <zeit.cms.workingcopy.workingcopy.Workingcopy object at 0x...>
Event: <zeit.cms.checkout.interfaces.AfterCheckoutEvent object at 0x...>
    Principal: zope.user
    Content: <zeit.cms.repository.unknown.PersistentUnknownResource object at 0x...>
    Workingcopy: <zeit.cms.workingcopy.workingcopy.Workingcopy object at 0x...>
>>> lockable.locked()
True 
>>> working_copy = checked_out.__parent__
>>> del working_copy[checked_out.__name__]
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
    Content: <zeit.cms.repository.unknown.PersistentUnknownResource object at 0x...>
    Workingcopy: <zeit.cms.workingcopy.workingcopy.Workingcopy object at 0x...>
Event: <zeit.cms.checkout.interfaces.AfterCheckoutEvent object at 0x...>
    Principal: zope.user
    Content: <zeit.cms.repository.unknown.PersistentUnknownResource object at 0x...>
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
[u'4schanzentournee-abgesang']


The lock timeout is small for temporary checkouts (around 30 seconds):

>>> lockable = zope.app.locking.interfaces.ILockable(content)
>>> lockable.locked()
True
>>> round(lockable.getLockInfo().timeout)
30.0

We can also check in the temporary checkout:

>>> manager = ICheckinManager(checked_out)
>>> manager.canCheckin
True
>>> manager.checkin()
Event: <zeit.cms.checkout.interfaces.BeforeCheckinEvent object at 0x...>
    Principal: zope.user
    Content: <zeit.cms.repository.unknown.PersistentUnknownResource object at 0x...>
    Workingcopy: <zeit.cms.workingcopy.workingcopy.Workingcopy object at 0x...>
Event: <zeit.cms.checkout.interfaces.AfterCheckinEvent object at 0x...>
    Principal: zope.user
    Content: <zeit.cms.repository.unknown.PersistentUnknownResource object at 0x...>
    Workingcopy: <zeit.cms.workingcopy.workingcopy.Workingcopy object at 0x...>
<zeit.cms.repository.unknown.PersistentUnknownResource object at 0x...>


Semantic changes
================

When an object is changed semantiacally (i.e. a user changed the text in
contrast to the system updating references) the ``semantic_change`` argument
must be True.

Initially there is no semantic change:

>>> import zeit.cms.content.interfaces
>>> sc = zeit.cms.content.interfaces.ISemanticChange(content)
>>> sc.last_semantic_change is None
True

After checking in with an semantic change the date is set:

>>> manager = ICheckoutManager(content)
>>> checked_out = manager.checkout()
Event:...
>>> manager = ICheckinManager(checked_out)
>>> manager.checkin(semantic_change=True)
Event...
>>> last_semantic_change = sc.last_semantic_change
>>> last_semantic_change
datetime.datetime(...)

Checking in without having ``semantic_change`` set to True will not change this
date:

>>> manager = ICheckoutManager(content)
>>> checked_out = manager.checkout()
Event:...
>>> manager = ICheckinManager(checked_out)
>>> manager.checkin()
Event...
>>> last_semantic_change == sc.last_semantic_change
True


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
>>> site_manager.registerUtility(
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

>>> site_manager.unregisterUtility(
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
...     zeit.cms.testcontenttype.testcontenttype.TestContentType())

Checking in is not possible just like that:

>>> ICheckinManager(checked_out).checkin()
Traceback (most recent call last):
    ...
ConflictError: There was a conflict while adding ${name}

Checking in is possible with ignored conflicts:

>>> ICheckinManager(checked_out).checkin(ignore_conflicts=True)
<zeit.cms.repository.unknown.PersistentUnknownResource object at 0x...>





.. [#functional]

    >>> import zeit.cms.testing
    >>> zeit.cms.testing.set_site()
