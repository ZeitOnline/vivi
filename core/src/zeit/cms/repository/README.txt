==========
Repository
==========

Browsing the repository works by folder classes which on the fly fetch data
from the backend. The interface to the backend is `os` like. 

We need to set the site since we're a functional test:

>>> import zope.app.component.hooks
>>> old_site = zope.app.component.hooks.getSite()
>>> zope.app.component.hooks.setSite(getRootFolder())


Repository Contaniers
=====================


The repository contains objects representing collections in the WebDAV server:

>>> import zope.component
>>> from zeit.cms.repository.interfaces import IRepository
>>> repository = zope.component.getUtility(IRepository)
>>> repository.keys()
[u'2006', u'2007', u'online', u'politik.feed', u'wirtschaft.feed']

>>> c_2007 = repository['online']['2007']
>>> c_2007
<zeit.cms.repository.repository.Folder object at 0x...>
>>> c_2007.keys()
[u'01', u'02']
>>> from pprint import pprint
>>> pprint(list(c_2007.values()))
[<zeit.cms.repository.repository.Folder object at 0x...>,
 <zeit.cms.repository.repository.Folder object at 0x...>]
>>> len(c_2007)
2
>>> pprint(list(c_2007.items()))
[(u'01', <zeit.cms.repository.repository.Folder object at 0x...>),
 (u'02', <zeit.cms.repository.repository.Folder object at 0x...>)]

>>> repository.get('2006')
<zeit.cms.repository.repository.Folder object at 0x...>
>>> print repository.get('2005')
None
>>> repository.get('2005', 'default')
'default' 


All objects in the the repository will also provide the IRepositoryContent
interface:

>>> from zeit.cms.repository.interfaces import IRepositoryContent
>>> IRepositoryContent.providedBy(c_2007)
True

 
Getting Content objects
=======================

We are getting the objects /online/2007/01/lebenslagen-01:

>>> content = repository['online']['2007']['01']['lebenslagen-01']
>>> content
<zeit.cms.repository.unknown.UnknownResource object at 0x...>


The content object provides IRepositoryContent since it was read from the 
repository:

>>> IRepositoryContent.providedBy(content)
True

It also provides the ICMSContent interface:
 
>>> from zeit.cms.interfaces import ICMSContent
>>> ICMSContent.providedBy(content)
True 

When we get the same object again, we *really* get the *same* object:

>>> content is repository['online']['2007']['01']['lebenslagen-01']
True

Unique Ids
==========

The CMS backend provides unique ids for content objects. The ids have the form
of `http://xml.zeit.de/(online)?/[Jahr]/[Ausgabe]/[Artikelname]` but that's
actually a backend implementation detail:

>>> content.uniqueId
u'http://xml.zeit.de/online/2007/01/lebenslagen-01'


Adding Content Objects
======================

Adding conntent objects to the repository requires them too be adaptable to
IResource. During adding also a unique id will be assigned if the object
doesn't have one yet. Let's create a new `UnknownResource`:

>>> from zeit.cms.repository.unknown import UnknownResource
>>> content = UnknownResource(u"I'm a shiny new object.")
>>> content.data
u"I'm a shiny new object."

The content does not have a unique id yet:

>>> print content.uniqueId
None

After adding it to the repository, it has a unique id:

>>> repository['i_am_new'] = content
>>> content.uniqueId
u'http://xml.zeit.de/i_am_new'

Since it does have an id we can get it back from the repository:

>>> new_content = repository.getUncontainedContent(content.uniqueId)
>>> new_content
<zeit.cms.repository.unknown.UnknownResource object at 0x...>
>>> new_content.data
u"I'm a shiny new object."


Deleting Content Object
=======================

Content can be deleted just like with any other container, using __delitem__:

>>> 'i_am_new' in repository
True
>>> del repository['i_am_new']
>>> 'i_am_new' in repository
False 

When you try to delete a non existend object, a KeyError is raised:

>>> del repository['i-dont-exist']
Traceback (most recent call last):
    ...
KeyError: "The resource u'http://xml.zeit.de/i-dont-exist' does not exist."


User Preferences
================

Users have different preferences regarding what to see and what not.
Preferences regarding the repository are stored in an `IUserPreferences`
objet. Login bob:

>>> import zope.security.management
>>> import zope.security.testing
>>> zope.security.management.endInteraction()
>>> principal = zope.security.testing.Principal(u'bob')
>>> participation = zope.security.testing.Participation(principal)
>>> zope.security.management.newInteraction(participation)

... and get his preferences:

>>> import zeit.cms.workingcopy.interfaces
>>> from zeit.cms.repository.interfaces import IUserPreferences
>>> location = zope.component.getUtility(
...     zeit.cms.workingcopy.interfaces.IWorkingcopyLocation)
>>> workingcopy = location.getWorkingcopy()
>>> preferences = IUserPreferences(workingcopy)
>>> preferences
<zeit.cms.repository.preference.UserPreferences object at 0x...>

Initially there is nothing hidden:

>>> preferences.hidden_containers
()


Logout bob again:

>>> zope.security.management.endInteraction()

Cleanup
=======

After tests we clean up:

>>> zope.app.component.hooks.setSite(old_site)
