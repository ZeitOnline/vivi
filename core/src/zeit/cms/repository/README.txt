==========
Repository
==========

Browsing the repository works by folder classes which on the fly fetch data
from the backend. The interface to the backend is `os` like. 

We need to set the site since we're a functional test:

>>> import zope.app.component.hooks
>>> old_site = zope.app.component.hooks.getSite()
>>> zope.app.component.hooks.setSite(getRootFolder())


Repository Containers
=====================

The repository contains objects representing collections in the WebDAV server:

>>> import zope.component
>>> from zeit.cms.repository.interfaces import IRepository
>>> repository = zope.component.getUtility(IRepository)
>>> repository.keys()
[u'online', u'2006', u'2007', u'politik.feed', u'testcontent',
 u'wirtschaft.feed']

>>> c_2007 = repository['online']['2007']
>>> c_2007
<zeit.cms.repository.folder.Folder object at 0x...>
>>> c_2007.keys()
[u'01', u'02']
>>> from pprint import pprint
>>> pprint(list(c_2007.values()))
[<zeit.cms.repository.folder.Folder object at 0x...>,
 <zeit.cms.repository.folder.Folder object at 0x...>]
>>> len(c_2007)
2
>>> pprint(list(c_2007.items()))
[(u'01', <zeit.cms.repository.folder.Folder object at 0x...>),
 (u'02', <zeit.cms.repository.folder.Folder object at 0x...>)]

>>> repository.get('2006')
<zeit.cms.repository.folder.Folder object at 0x...>
>>> print repository.get('2005')
None
>>> repository.get('2005', 'default')
'default' 


All objects in the the repository will also provide the IRepositoryContent
interface:

>>> from zeit.cms.repository.interfaces import IRepositoryContent
>>> IRepositoryContent.providedBy(c_2007)
True

The repository itself provides IRepositoryContent too:

>>> IRepositoryContent.providedBy(repository)
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


Unknown Resource
================

We got an UnknownResource object from the repository, because the system
doesn't know anything else to do with this content. The resource has webdav
properties:

>>> import zeit.connector.interfaces
>>> properties = zeit.connector.interfaces.IWebDAVReadProperties(content)
>>> properties
<zeit.cms.content.liveproperty.LiveProperties object at 0x...>
>>> pprint(dict(properties))
{('DailyNL', 'http://namespaces.zeit.de/CMS/workflow'): 'no',
 ('author', 'http://namespaces.zeit.de/CMS/document'): ' Thomas Luther',
 ('banner', 'http://namespaces.zeit.de/CMS/document'): 'yes',
 ('comments', 'http://namespaces.zeit.de/CMS/document'): '1',
 ('copyrights', 'http://namespaces.zeit.de/CMS/document'): 'ZEIT online',
 ('date-last-modified', 'http://namespaces.zeit.de/CMS/document'): '4.1.2007 - 14:16',
 ('erscheint', 'http://namespaces.zeit.de/CMS/document'): None,
 ('getlastmodified', 'DAV:'): u'Fri, 07 Mar 2008 12:47:16 GMT',
 ('imagecount', 'http://namespaces.zeit.de/CMS/document'): '0',
 ('keywords', 'http://namespaces.zeit.de/CMS/document'): 'GEBO; anlageberater; Versicherungen; provision; finanzberater;',
 ('last-modified-by', 'http://namespaces.zeit.de/CMS/workflow'): 'hegenscheidt',
 ('mostread', 'http://namespaces.zeit.de/CMS/document'): 'yes',
 ('new_comments', 'http://namespaces.zeit.de/CMS/document'): '1',
 ('page', 'http://namespaces.zeit.de/CMS/document'): '-',
 ('page', 'http://namespaces.zeit.de/QPS/attributes'): '-',
 ('pagelabel', 'http://namespaces.zeit.de/CMS/document'): 'Online',
 ('paragraphsperpage', 'http://namespaces.zeit.de/CMS/document'): '4',
 ('ressort', 'http://namespaces.zeit.de/CMS/document'): 'Finanzen',
 ('ressort', 'http://namespaces.zeit.de/QPS/attributes'): 'Online',
 ('revision', 'http://namespaces.zeit.de/CMS/document'): '5',
 ('serie', 'http://namespaces.zeit.de/CMS/document'): '-',
 ('status', 'http://namespaces.zeit.de/CMS/workflow'): 'OK',
 ('supertitle', 'http://namespaces.zeit.de/CMS/document'): 'Spitzmarke hierher',
 ('text-length', 'http://namespaces.zeit.de/CMS/document'): '1036',
 ('title', 'http://namespaces.zeit.de/CMS/document'): 'Kampf der Provisionsschinderei',
 ('topic', 'http://namespaces.zeit.de/CMS/document'): 'Wirtschaft',
 ('type', 'http://namespaces.zeit.de/CMS/document'): 'article',
 ('type', 'http://namespaces.zeit.de/CMS/meta'): 'article',
 ('volume', 'http://namespaces.zeit.de/CMS/document'): '01',
 ('volume', 'http://namespaces.zeit.de/QPS/attributes'): '04',
 ('year', 'http://namespaces.zeit.de/CMS/document'): '2007',
 ('year', 'http://namespaces.zeit.de/QPS/attributes'): '2006'}


When we convert the UnknownResource back to a `Resource` object, the properties
are still there:

>>> resource = zeit.connector.interfaces.IResource(content)
>>> resource
<zeit.connector.resource.Resource object at 0x...>
>>> resource.properties
<zeit.connector.resource.WebDAVProperties object at 0x...>
>>> pprint(dict(resource.properties))
{('DailyNL', 'http://namespaces.zeit.de/CMS/workflow'): 'no',
 ('author', 'http://namespaces.zeit.de/CMS/document'): ' Thomas Luther',
 ('banner', 'http://namespaces.zeit.de/CMS/document'): 'yes',
 ('comments', 'http://namespaces.zeit.de/CMS/document'): '1',
 ('copyrights', 'http://namespaces.zeit.de/CMS/document'): 'ZEIT online',
 ('date-last-modified', 'http://namespaces.zeit.de/CMS/document'): '4.1.2007 - 14:16',
 ('erscheint', 'http://namespaces.zeit.de/CMS/document'): None,
 ('getlastmodified', 'DAV:'): u'Fri, 07 Mar 2008 12:47:16 GMT',
 ('imagecount', 'http://namespaces.zeit.de/CMS/document'): '0',
 ('keywords', 'http://namespaces.zeit.de/CMS/document'): 'GEBO; anlageberater; Versicherungen; provision; finanzberater;',
 ('last-modified-by', 'http://namespaces.zeit.de/CMS/workflow'): 'hegenscheidt',
 ('mostread', 'http://namespaces.zeit.de/CMS/document'): 'yes',
 ('new_comments', 'http://namespaces.zeit.de/CMS/document'): '1',
 ('page', 'http://namespaces.zeit.de/CMS/document'): '-',
 ('page', 'http://namespaces.zeit.de/QPS/attributes'): '-',
 ('pagelabel', 'http://namespaces.zeit.de/CMS/document'): 'Online',
 ('paragraphsperpage', 'http://namespaces.zeit.de/CMS/document'): '4',
 ('ressort', 'http://namespaces.zeit.de/CMS/document'): 'Finanzen',
 ('ressort', 'http://namespaces.zeit.de/QPS/attributes'): 'Online',
 ('revision', 'http://namespaces.zeit.de/CMS/document'): '5',
 ('serie', 'http://namespaces.zeit.de/CMS/document'): '-',
 ('status', 'http://namespaces.zeit.de/CMS/workflow'): 'OK',
 ('supertitle', 'http://namespaces.zeit.de/CMS/document'): 'Spitzmarke hierher',
 ('text-length', 'http://namespaces.zeit.de/CMS/document'): '1036',
 ('title', 'http://namespaces.zeit.de/CMS/document'): 'Kampf der Provisionsschinderei',
 ('topic', 'http://namespaces.zeit.de/CMS/document'): 'Wirtschaft',
 ('type', 'http://namespaces.zeit.de/CMS/document'): 'article',
 ('type', 'http://namespaces.zeit.de/CMS/meta'): 'article',
 ('volume', 'http://namespaces.zeit.de/CMS/document'): '01',
 ('volume', 'http://namespaces.zeit.de/QPS/attributes'): '04',
 ('year', 'http://namespaces.zeit.de/CMS/document'): '2007',
 ('year', 'http://namespaces.zeit.de/QPS/attributes'): '2006'}

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


Renaming objects
================

Objects can be renamed in a container using IContainerItemRenamer:

>>> import zope.copypastemove.interfaces
>>> renamer = zope.copypastemove.interfaces.IContainerItemRenamer(repository)
>>> renamer.renameItem('i_am_new', 'i_am_not_so_new_anymore')
>>> list(repository)
[u'online', u'2006', u'2007', u'i_am_not_so_new_anymore', u'politik.feed',
 u'testcontent', u'wirtschaft.feed']

Rename it back:

>>> renamer.renameItem('i_am_not_so_new_anymore', 'i_am_new')
>>> list(repository)
[u'online', u'2006', u'2007', u'i_am_new', u'politik.feed',
 u'testcontent', u'wirtschaft.feed']


Deleting Content Object
=======================

Content can be deleted just like with any other container, using __delitem__:

>>> 'i_am_new' in repository
True
>>> del repository['i_am_new']
>>> 'i_am_new' in repository
False 

Getting the value of course doesn't work either:

>>> repository['i_am_new']
Traceback (most recent call last):
    ...
KeyError: u'http://xml.zeit.de/i_am_new'


When you try to delete a non existend object, a KeyError is raised:

>>> del repository['i-dont-exist']
Traceback (most recent call last):
    ...
KeyError: "The resource u'http://xml.zeit.de/i-dont-exist' does not exist."


Copying objects
===============

It is possible to copy objects using the IObjectCopier interface. Get an object
to copy:

>>> to_copy = repository['online']['2007']['01']

Get the copier:

>>> import zope.interface.verify
>>> copier = zope.copypastemove.interfaces.IObjectCopier(to_copy)
>>> zope.interface.verify.verifyObject(
...     zope.copypastemove.interfaces.IObjectCopier, copier)
True
>>> copier.copyable()
True
>>> copier.copyableTo(repository)
True
>>> copier.copyableTo(repository, name=u'foo')
True

Let's copy. `copyTo` returns the new name:

>>> copier.copyTo(repository['online'])
u'01'

When copying againer, we'll get another name:

>>> copier.copyTo(repository['online'])
u'01-2'

>>> repository['online'].keys()
[u'01', u'01-2', u'2005', u'2006', u'2007']
>>> len(repository['online']['01'].keys())
53

Let's clean that up again:

>>> del repository['online']['01']
>>> del repository['online']['01-2']


Getting content by unique_id
============================

The `getContent` method of IRepository returns the contained content object
from the unique id:

>>> content = repository.getContent(
...     'http://xml.zeit.de/online/2007/01/Somalia')
>>> content
<zeit.cms.repository.unknown.UnknownResource object at 0x...>
>>> content.__parent__
<zeit.cms.repository.folder.Folder object at 0x...>
>>> content.__parent__.__name__
u'01'


A TypeError is raised if anything but a string is passed:

>>> repository.getContent(None)
Traceback (most recent call last):
    ...
TypeError: unique_id: string expected, got <type 'NoneType'>

>>> repository.getContent(123)
Traceback (most recent call last):
    ...
TypeError: unique_id: string expected, got <type 'int'>


A ValueError is raised if the unique_id doesn't start with the configured
prefix of http://xml.zeit.de:

>>> repository.getContent('foo')
Traceback (most recent call last):
    ...
ValueError: The id 'foo' is invalid.


A KeyError is raised if the unique_id does not reference to an existing object:

>>> repository.getContent('http://xml.zeit.de/online/foo')
Traceback (most recent call last):
    ...
KeyError: 'http://xml.zeit.de/online/foo'


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


There is a list of containers which are shown by default:

>>> pprint(preferences.default_shown_containers)
('http://xml.zeit.de/repository/2007',
 'http://xml.zeit.de/repository/2008',
 'http://xml.zeit.de/repository/bilder',
 'http://xml.zeit.de/repository/bilder/2007',
 'http://xml.zeit.de/repository/bilder/2008',
 'http://xml.zeit.de/repository/hp_channels',
 'http://xml.zeit.de/repository/online',
 'http://xml.zeit.de/repository/online/2007',
 'http://xml.zeit.de/repository/online/2008',
 'http://xml.zeit.de/repository/themen')


From this list the default hidden_containers are derifed uppon instanciation.
So everything which is not noted in the `default_shown_containers`:

>>> pprint(sorted(preferences._hidden_containers))
[u'http://xml.zeit.de/2006',
 u'http://xml.zeit.de/online/2005',
 u'http://xml.zeit.de/online/2006',
 u'http://xml.zeit.de/politik.feed',
 u'http://xml.zeit.de/testcontent',
 u'http://xml.zeit.de/wirtschaft.feed']


Let's see if is_hidden works:

>>> preferences.is_hidden(repository['online']['2005'])
True
>>> preferences.is_hidden(repository['online']['2007'])
False

Let's show a container:

>>> preferences.show_container(repository['online']['2005'])
>>> preferences.is_hidden(repository['online']['2005'])
False

Double show doesn't harm:

>>> preferences.show_container(repository['online']['2005'])
>>> preferences.is_hidden(repository['online']['2005'])
False


Let's hide it again:

>>> preferences.hide_container(repository['online']['2005'])
>>> preferences.is_hidden(repository['online']['2005'])
True

Double hide dosn't harm as well:

>>> preferences.hide_container(repository['online']['2005'])
>>> preferences.is_hidden(repository['online']['2005'])
True

Logout bob again:

>>> zope.security.management.endInteraction()


Cleanup
=======

After tests we clean up:

>>> zope.app.component.hooks.setSite(old_site)
