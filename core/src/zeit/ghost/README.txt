======
Ghosts
======

Ghosts haunt other objects. We use this to put ghosts in the workingcopy after
an object has been checked in. The checked in object will be replaced by a
ghost, allowing the user to easily access objects he recently edited.

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()
>>> principal = zeit.cms.testing.create_interaction()

In fact we do have those ghosts already in the clipboard, so we just reuse it.

Get the workingcopy, initially it's empty

>>> from zeit.cms.workingcopy.interfaces import IWorkingcopy
>>> workingcopy = IWorkingcopy(principal)
>>> list(workingcopy.keys())
[]

When we check out an object now, it'll populate the workingcopy:

>>> from zeit.cms.repository.interfaces import IRepository
>>> import zope.component
>>> repository = zope.component.getUtility(IRepository)
>>> collection = repository['online']['2007']['01']
>>> content = list(collection.values())[0]
>>> from zeit.cms.checkout.interfaces import (
...     ICheckoutManager, ICheckinManager)
>>> manager = ICheckoutManager(content)
>>> checked_out = manager.checkout()
>>> list(workingcopy.keys())
['4schanzentournee-abgesang']


When we checkin now, a ghost will populate the workingcopy:


>>> manager = ICheckinManager(checked_out)
>>> checked_in = manager.checkin()
>>> list(workingcopy.keys())
['4schanzentournee-abgesang']


Get the ghost from the workingcopy:

>>> ghost = workingcopy['4schanzentournee-abgesang']
>>> ghost
<zeit.cms.clipboard.entry.Entry...>

When we check out the content object again, the ghost is replaced by the
checked out object:

>>> checked_out = ICheckoutManager(content).checkout()
>>> list(workingcopy.keys())
['4schanzentournee-abgesang-2']

Note that we have a different local name in the workingcopy. But this doesn't
matter and is not really visible for the user anyway. The uniqueId is correct
though:

>>> checked_out.__name__
'4schanzentournee-abgesang-2'
>>> checked_out.uniqueId
'http://xml.zeit.de/online/2007/01/4schanzentournee-abgesang'

When we do a temporary checkout no ghost will be added to the workingcopy:

>>> manager = ICheckoutManager(collection['Flugsicherheit'])
>>> checked_out = manager.checkout(temporary=True)
>>> manager = ICheckinManager(checked_out)
>>> manager.checkin()
<zeit.cms.repository.unknown.PersistentUnknownResource...>
>>> list(workingcopy.keys())
['4schanzentournee-abgesang-2']

Automatic ghost removing
========================

The workingcopy has a target size of 7. This means that when the 8th object is
checked out, a ghosts will be removed until the workingcopy size is less that 8
or there are no more ghosts.

Check out objects until we have 7 in the working copy:

>>> for name in collection.keys()[1:]:
...     print(name)
...     content = collection[name]
...     manager = ICheckoutManager(content)
...     co = manager.checkout()
...     if len(workingcopy) >= 7:
...         break
Arbeitsmarktzahlen
EU-Beitritt-rumaenien-bulgarien
Flugsicherheit
Ford-Beerdigung
Gesundheitsreform-Die
Guantanamo


Create a little helper function to easily see what is a ghost and what not:

>>> import zeit.cms.clipboard.interfaces
>>> def list_workingcopy():
...     print("%s entries" % len(workingcopy))
...     for name in workingcopy:
...         if zeit.cms.clipboard.interfaces.IObjectReference.providedBy(
...             workingcopy[name]):
...             typ = "Ghost  : "
...         else:
...             typ = "Content: "
...         print(typ + name)


>>> list_workingcopy()
7 entries
Content: Guantanamo
Content: Gesundheitsreform-Die
Content: Ford-Beerdigung
Content: Flugsicherheit
Content: EU-Beitritt-rumaenien-bulgarien
Content: Arbeitsmarktzahlen
Content: 4schanzentournee-abgesang-2


Checkin Flugsicherheit and Arbeitsmarktzahlen:

>>> checked_in = ICheckinManager(workingcopy['Flugsicherheit']).checkin()
>>> checked_in = ICheckinManager(workingcopy['Arbeitsmarktzahlen']).checkin()
>>> list_workingcopy()
7 entries
Ghost  : Arbeitsmarktzahlen
Ghost  : Flugsicherheit
Content: Guantanamo
Content: Gesundheitsreform-Die
Content: Ford-Beerdigung
Content: EU-Beitritt-rumaenien-bulgarien
Content: 4schanzentournee-abgesang-2


We have  exactly 7 objects in the workingcopy which is our target size. When we
check out another object the oldest ghost will be removed, Arbeitsmarktzahlen
in our case:

>>> checked_out = ICheckoutManager(collection['Querdax']).checkout()
>>> list_workingcopy()
7 entries
Content: Querdax
Ghost  : Arbeitsmarktzahlen
Content: Guantanamo
Content: Gesundheitsreform-Die
Content: Ford-Beerdigung
Content: EU-Beitritt-rumaenien-bulgarien
Content: 4schanzentournee-abgesang-2

When we checkout yet another object, the last remaining ghost will be removed:

>>> checked_out = ICheckoutManager(collection['Saarland']).checkout()
>>> list_workingcopy()
7 entries
Content: Saarland
Content: Querdax
Content: Guantanamo
Content: Gesundheitsreform-Die
Content: Ford-Beerdigung
Content: EU-Beitritt-rumaenien-bulgarien
Content: 4schanzentournee-abgesang-2


After checking out another object, we'll have 8 objects int he workingcopy as
there is no ghost to remove:

>>> checked_out = ICheckoutManager(collection['Somalia']).checkout()
>>> list_workingcopy()
8 entries
Content: Somalia
Content: Saarland
Content: Querdax
Content: Guantanamo
Content: Gesundheitsreform-Die
Content: Ford-Beerdigung
Content: EU-Beitritt-rumaenien-bulgarien
Content: 4schanzentournee-abgesang-2

When we check in a content now, we'll have a ghost despite the target size of
7:

>>> checked_in = ICheckinManager(workingcopy['Gesundheitsreform-Die']
...     ).checkin()
>>> list_workingcopy()
8 entries
Ghost  : Gesundheitsreform-Die
Content: Somalia
Content: Saarland
Content: Querdax
Content: Guantanamo
Content: Ford-Beerdigung
Content: EU-Beitritt-rumaenien-bulgarien
Content: 4schanzentournee-abgesang-2

Checking in another object, still does not remove any ghost:

>>> checked_in = ICheckinManager(workingcopy['Querdax']
...     ).checkin()
>>> list_workingcopy()
8 entries
Ghost  : Querdax
Ghost  : Gesundheitsreform-Die
Content: Somalia
Content: Saarland
Content: Guantanamo
Content: Ford-Beerdigung
Content: EU-Beitritt-rumaenien-bulgarien
Content: 4schanzentournee-abgesang-2

Note that any invalid ghosts, that are ghosts which reference deleted objects,
are also removed when checking out any object.

First make some space in the workingcopy to avoid side effects like deleting
overflowing ghosts:

>>> del workingcopy['Ford-Beerdigung']
>>> del workingcopy['Somalia']

Now delete Querdax in the repository:

>>> del collection['Querdax']

So far nothing has happend to the Querdax entry:

>>> list_workingcopy()
6 entries
Ghost  : Querdax
Ghost  : Gesundheitsreform-Die
Content: Saarland
Content: Guantanamo
Content: EU-Beitritt-rumaenien-bulgarien
Content: 4schanzentournee-abgesang-2



When we checkout an object now, the invalid ghost Querdax will be removed:

>>> checked_out = ICheckoutManager(collection['Ford-Beerdigung']).checkout()
>>> list_workingcopy()
6 entries
Content: Ford-Beerdigung
Ghost  : Gesundheitsreform-Die
Content: Saarland
Content: Guantanamo
Content: EU-Beitritt-rumaenien-bulgarien
Content: 4schanzentournee-abgesang-2
