============
Working Copy
============

The working copy is the area of the CMS where users actually edit content. 

First we register the location utility:

>>> import zope.component
>>> import zope.interface.verify
>>> from zeit.cms.workingcopy.interfaces import IWorkingcopyLocation
>>> from zeit.cms.workingcopy.workingcopy import WorkingcopyLocation
>>> zope.interface.verify.verifyClass(
...     IWorkingcopyLocation, WorkingcopyLocation)
True
>>> site_manager = zope.component.getSiteManager()
>>> location = WorkingcopyLocation()
>>> site_manager.registerUtility(location, IWorkingcopyLocation)

We also need a principal permission manager:

>>> class PPM(object):
...
...     def __init__(self, context):
...         self.context = context
...
...     def grantPermissionToPrincipal(self, permission, principal):
...         print "Granting %s to %s" % (permission, principal)
...
>>> import zope.securitypolicy.interfaces
>>> site_manager.registerAdapter(
...   PPM, (zope.interface.Interface, ),
...   zope.securitypolicy.interfaces.IPrincipalPermissionManager)

And we need a principal role manager:

>>> class PRM(object):
...
...     def __init__(self, context):
...         self.context = context
...
...     def assignRoleToPrincipal(self, role, principal):
...         print "Assigning role %s to %s" % (role, principal)
...
>>> site_manager.registerAdapter(
...   PRM, (zope.interface.Interface, ),
...   zope.securitypolicy.interfaces.IPrincipalRoleManager)


Adapting Principals
===================

Since every user has his own working area we have an adapter from IPrincipal to
IWorkingcopy. The working copy is created implicitly. This becomes visible by
the "Granting ..." messages:

>>> from zeit.cms.workingcopy.workingcopy import principalAdapter
>>> class Principal:
...     id = 'hans'
...
>>> principal = Principal()
>>> workingcopy = principalAdapter(principal)
Granting zeit.EditContent to hans
Assigning role zeit.Owner to hans
>>> workingcopy
<zeit.cms.workingcopy.workingcopy.Workingcopy object at 0x...>


During adaptaion the Workingcopy object was automatically be added to the
location:

>>> print list(location.keys())
[u'hans']
>>> location[u'hans'] is workingcopy
True


When we adapt the Principal again, we'll also get the same workingcopy:

>>> workingcopy is principalAdapter(principal)
True


Getting the Workingcopy of the Currently Logged in User
=======================================================

Getting the Workingcopy of the currently logged in user is done by the
`getWorkingCopy` method of `WorkingcopyLocation`. Log in `kurt` and get his
workingcopy: 

>>> import zope.security.testing
>>> principal = zope.security.testing.Principal('kurt')
>>> participation = zope.security.testing.Participation(principal)
>>> import zope.security.management
>>> zope.security.management.newInteraction(participation)

>>> workingcopy = location.getWorkingcopy()
Granting zeit.EditContent to kurt
Assigning role zeit.Owner to kurt
>>> workingcopy
<zeit.cms.workingcopy.workingcopy.Workingcopy object at 0x...>
>>> workingcopy.__name__
u'kurt'
>>> print sorted(location.keys())
[u'hans', u'kurt']
>>> zope.security.management.endInteraction()


Identifying Local Content
=========================

Only content which provides ILocalContent can be added to the workingcopy:

>>> from zeit.cms.workingcopy.interfaces import ILocalContent
>>> from zeit.cms.repository.unknown import UnknownResource
>>> content = UnknownResource(u'oink')
>>> ILocalContent.providedBy(content)
False
>>> workingcopy[u'mycontent'] = content
Traceback (most recent call last):
    ...
ValueError: Must provide ILocalContent

After marking as ILocalContent it can be added:

>>> zope.interface.directlyProvides(content, ILocalContent)
>>> workingcopy[u'mycontent'] = content
>>> ILocalContent.providedBy(content)
True 

Sorting
=======

When things are added to the workingcopy they are returned in reverse order.
Currently there is only one object in the database:

>>> list(workingcopy)
[u'mycontent']

Let's add another content:

>>> content = UnknownResource(u'oink')
>>> zope.interface.directlyProvides(content, ILocalContent)
>>> workingcopy[u'other-content'] = content
>>> list(workingcopy)
[u'other-content', u'mycontent']
>>> [v.__name__ for v in workingcopy.values()]
[u'other-content', u'mycontent']

Add another content:

>>> content = UnknownResource(u'oink')
>>> zope.interface.directlyProvides(content, ILocalContent)
>>> workingcopy[u'just-another-content'] = content
>>> list(workingcopy)
[u'just-another-content', u'other-content', u'mycontent']
>>> [v.__name__ for v in workingcopy.values()]
[u'just-another-content', u'other-content', u'mycontent']


Remove `other-content`:

>>> del workingcopy[u'other-content']
>>> list(workingcopy)
[u'just-another-content', u'mycontent']
>>> [v.__name__ for v in workingcopy.values()]
[u'just-another-content', u'mycontent']


Cleanup
=======

Cleanup after test:

>>> site_manager.unregisterUtility(location, IWorkingcopyLocation)
True
>>> site_manager.unregisterAdapter(
...   PPM, (zope.interface.Interface, ),
...   zope.securitypolicy.interfaces.IPrincipalPermissionManager)
True
>>> site_manager.unregisterAdapter(
...   PRM, (zope.interface.Interface, ),
...   zope.securitypolicy.interfaces.IPrincipalRoleManager)
True
