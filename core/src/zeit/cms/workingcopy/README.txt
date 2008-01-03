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

We also need an principal permission manager:

>>> class PPM(object):
...
...     def __init__(self, context):
...         self.context = context
...
...     def grantPermissionToPrincipal(self, permission, principal):
...         print "Granting %s to %s" % (permission, principal)
...
>>> site_manager.registerAdapter(
...   PPM, (zope.interface.Interface, ),
...   zope.app.securitypolicy.interfaces.IPrincipalPermissionManager)


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
Granting zope.ManageContent to hans
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
Granting zope.ManageContent to kurt
>>> workingcopy
<zeit.cms.workingcopy.workingcopy.Workingcopy object at 0x...>
>>> workingcopy.__name__
u'kurt'
>>> print sorted(location.keys())
[u'hans', u'kurt']
>>> zope.security.management.endInteraction()


Identifying Local Content
=========================


Content in the working copy provides the `ILocalContent` interface:

>>> from zeit.cms.workingcopy.interfaces import ILocalContent
>>> from zeit.cms.repository.unknown import UnknownResource
>>> content = UnknownResource(u'oink')
>>> ILocalContent.providedBy(content)
False
>>> workingcopy['mycontent'] = content
>>> ILocalContent.providedBy(content)
True 


Cleanup
=======

Cleanup after test:

>>> site_manager.unregisterUtility(location, IWorkingcopyLocation)
True
>>> site_manager.unregisterAdapter(
...   PPM, (zope.interface.Interface, ),
...   zope.app.securitypolicy.interfaces.IPrincipalPermissionManager)
True
