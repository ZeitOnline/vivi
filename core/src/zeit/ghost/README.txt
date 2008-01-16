======
Ghosts
======

Ghosts haunt other objects. We use this to put ghosts in the workingcopy after
an object has been checked in. The checked in object will be replaced by a
ghost, allowing the user to easily access objects he recently edited.


In fact we do have those ghosts already in the clipboard, so we just reuse it.

Do some setup for the functional test:

>>> import zope.app.component.hooks
>>> old_site = zope.app.component.hooks.getSite()
>>> zope.app.component.hooks.setSite(getRootFolder())


Login a user to have the full workingcopy context:

>>> import zope.security.testing
>>> principal = zope.security.testing.Principal(u'zope.user')
>>> participation = zope.security.testing.Participation(principal)
>>> import zope.security.management
>>> zope.security.management.newInteraction(participation)


Get the workingcopy, initially it's empty

>>> from zeit.cms.workingcopy.interfaces import IWorkingcopy
>>> workingcopy = IWorkingcopy(principal)
>>> list(workingcopy.keys())
[]

When we check out an object now, it'll populate the workingcopy:

>>> from zeit.cms.repository.interfaces import IRepository
>>> repository = zope.component.getUtility(IRepository)
>>> collection = repository['online']['2007']['01']
>>> content = list(collection.values())[0]
>>> from zeit.cms.checkout.interfaces import (
...     ICheckoutManager, ICheckinManager)
>>> manager = ICheckoutManager(content)
>>> checked_out = manager.checkout()
>>> list(workingcopy.keys())
[u'4schanzentournee-abgesang']


When we checkin now, a ghost will poulate the workingcopy:


>>> manager = ICheckinManager(checked_out)
>>> checked_in = manager.checkin()
>>> list(workingcopy.keys())
[u'4schanzentournee-abgesang']


Get the ghost from the workingcopy:

>>> ghost = workingcopy['4schanzentournee-abgesang']
>>> ghost
<zeit.cms.clipboard.entry.Entry object at 0x...>



Cleanup
=======

>>> zope.app.component.hooks.setSite(old_site)
