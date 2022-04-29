==========
Repository
==========

Browsing the repository works by folder classes which on the fly fetch data
from the backend. The interface to the backend is `os` like.

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()

Repository Containers
=====================

The repository contains objects representing collections in the WebDAV server:

>>> import zope.component
>>> from zeit.cms.repository.interfaces import IRepository
>>> repository = zope.component.getUtility(IRepository)
>>> 'online' in repository.keys()
True

>>> c_2007 = repository['online']['2007']
>>> c_2007
<zeit.cms.repository.folder.Folder...>
>>> c_2007.keys()
['01', '02']
>>> from pprint import pprint
>>> pprint(list(c_2007.values()))
[<zeit.cms.repository.folder.Folder...>,
 <zeit.cms.repository.folder.Folder...>]
>>> len(c_2007)
2
>>> pprint(list(c_2007.items()))
[('01', <zeit.cms.repository.folder.Folder...>),
 ('02', <zeit.cms.repository.folder.Folder...>)]

>>> repository.get('2006')
<zeit.cms.repository.folder.Folder...>
>>> print(repository.get('2005'))
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

Constructing objects sends an event. Create a handler to test this:

>>> import zeit.cms.interfaces
>>> def after_construct(object, event):
...     print("Constructing %s" % object.uniqueId)
...     site_manager.unregisterHandler(
...         after_construct,
...         (zeit.cms.interfaces.ICMSContent,
...          zeit.cms.repository.interfaces.IAfterObjectConstructedEvent))
>>> site_manager = zope.component.getSiteManager()
>>> site_manager.registerHandler(
...     after_construct,
...     (zeit.cms.interfaces.ICMSContent,
...      zeit.cms.repository.interfaces.IAfterObjectConstructedEvent))

Getting the object /online/2007/01/lebenslagen-01:

>>> content = repository['online']['2007']['01']['lebenslagen-01']
Constructing http://xml.zeit.de/online/2007/01/lebenslagen-01
>>> content
<zeit.cms.repository.unknown.PersistentUnknownResource...>


The content object provides IRepositoryContent since it was read from the
repository:

>>> IRepositoryContent.providedBy(content)
True

It also provides the ICMSContent interface:

>>> import zope.interface.verify
>>> zope.interface.verify.verifyObject(
...     zeit.cms.interfaces.ICMSContent, content)
True

We consider UnknownResources as editorial content (at least in the tests):

>>> zope.interface.verify.verifyObject(
...     zeit.cms.interfaces.IEditorialContent, content)
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
<zeit.cms.content.liveproperty.LiveProperties...>
>>> pprint(dict(properties))
{('author', 'http://namespaces.zeit.de/CMS/document'): ' Thomas Luther',
 ('banner', 'http://namespaces.zeit.de/CMS/document'): 'yes',
 ...


When we convert the PersistentUnknownResource back to a `Resource` object, the properties
are still there:

>>> resource = zeit.connector.interfaces.IResource(content)
>>> resource
<zeit.connector.resource.Resource...>
>>> resource.properties
<zeit.connector.resource.WebDAVProperties...>
>>> pprint(dict(resource.properties))
{('author', 'http://namespaces.zeit.de/CMS/document'): ' Thomas Luther',
 ('banner', 'http://namespaces.zeit.de/CMS/document'): 'yes',
 ...

Unique Ids
==========

The CMS backend provides unique ids for content objects. The ids have the form
of `http://xml.zeit.de/(online)?/[Jahr]/[Ausgabe]/[Artikelname]` but that's
actually a backend implementation detail:

>>> content.uniqueId
'http://xml.zeit.de/online/2007/01/lebenslagen-01'


Adding Content Objects
======================

Adding conntent objects to the repository requires them too be adaptable to
IResource. During adding also a unique id will be assigned if the object
doesn't have one yet. Let's create a new `PersistentUnknownResource`:

>>> from zeit.cms.repository.unknown import PersistentUnknownResource
>>> content = PersistentUnknownResource("I'm a shiny new object.")
>>> content.data
"I'm a shiny new object."

The content does not have a unique id yet:

>>> print(content.uniqueId)
None

Adding sends an event. Register an event handler for IBeforeObjectAddedEvent

>>> def before_added(object, event):
...     print("Before add: %s" % object)
>>> def added(object, event):
...     print('%s %s' % (type(event).__name__, object))
...     print('    Old: %s %s' % (event.oldParent, event.oldName))
...     print('    New: %s %s' % (event.newParent, event.newName))
>>> site_manager = zope.component.getSiteManager()
>>> site_manager.registerHandler(
...     before_added,
...     (zeit.cms.interfaces.ICMSContent,
...      zeit.cms.repository.interfaces.IBeforeObjectAddEvent))
>>> site_manager.registerHandler(
...     added,
...     (zeit.cms.interfaces.ICMSContent,
...      zope.lifecycleevent.interfaces.IObjectMovedEvent))

After adding it to the repository, it has a unique id:

>>> repository['i_am_new'] = content
Before add: <zeit.cms.repository.unknown.PersistentUnknownResource...>
ObjectAddedEvent <zeit.cms.repository.unknown.PersistentUnknownResource...>
    Old: None None
    New: <zeit.cms.repository.repository.Repository...> i_am_new
>>> content.uniqueId
'http://xml.zeit.de/i_am_new'

Since it does have an id we can get it back from the repository:

>>> new_content = repository.getContent(content.uniqueId)
>>> new_content
<zeit.cms.repository.unknown.PersistentUnknownResource...>
>>> new_content.data
"I'm a shiny new object."


Adding it again will store it again on the DAV (i.e. overwrite). An
IObjectAddedEvent is *not* sent:

>>> repository['i_am_new'] = new_content
Before add: <zeit.cms.repository.unknown.PersistentUnknownResource...>

>>> site_manager.unregisterHandler(
...         before_added,
...         (zeit.cms.interfaces.ICMSContent,
...          zeit.cms.repository.interfaces.IBeforeObjectAddEvent))
True


Renaming objects
================

Objects can be renamed in a container using IContainerItemRenamer:

>>> import zope.copypastemove.interfaces
>>> renamer = zope.copypastemove.interfaces.IContainerItemRenamer(repository)
>>> renamer.renameItem('i_am_new', 'i_am_not_so_new_anymore')
ObjectMovedEvent <zeit.cms.repository.unknown.PersistentUnknownResource...>
    Old: <zeit.cms.repository.repository.Repository...> i_am_new
    New: <zeit.cms.repository.repository.Repository...> i_am_not_so_new_anymore
'i_am_not_so_new_anymore'

>>> 'i_am_new' in repository
False
>>> 'i_am_not_so_new_anymore' in repository
True

Rename it back:

>>> renamer.renameItem('i_am_not_so_new_anymore', 'i_am_new')
ObjectMovedEvent...
>>> 'i_am_new' in repository
True
>>> 'i_am_not_so_new_anymore' in repository
False


Deleting Content Object
=======================

Deleting objects sends an event:

>>> import zeit.cms.interfaces
>>> def after_remove(object, event):
...     print("Deleting %s" % object.uniqueId)
...     site_manager.unregisterHandler(
...         after_remove,
...         (zeit.cms.interfaces.ICMSContent,
...          zeit.cms.repository.interfaces.IBeforeObjectRemovedEvent))
>>> site_manager = zope.component.getSiteManager()
>>> site_manager.registerHandler(
...     after_remove,
...     (zeit.cms.interfaces.ICMSContent,
...      zeit.cms.repository.interfaces.IBeforeObjectRemovedEvent))


Content can be deleted just like with any other container, using
__delitem__:

>>> 'i_am_new' in repository
True
>>> del repository['i_am_new']
BeforeObjectRemovedEvent <zeit.cms.repository.unknown.PersistentUnknownResource...>
    Old: <zeit.cms.repository.repository.Repository...> i_am_new
    New: None None
Deleting http://xml.zeit.de/i_am_new
>>> 'i_am_new' in repository
False

Getting the value of course doesn't work either:

>>> repository['i_am_new']
Traceback (most recent call last):
    ...
KeyError: 'http://xml.zeit.de/i_am_new'


When you try to delete a non existend object, a KeyError is raised:

>>> del repository['i-dont-exist']
Traceback (most recent call last):
    ...
KeyError: "The resource 'http://xml.zeit.de/i-dont-exist' does not exist."


Copying objects
===============

It is possible to copy objects using the IObjectCopier interface. Get an object
to copy:

>>> to_copy = repository['online']['2007']['01']

Get the copier:

>>> copier = zope.copypastemove.interfaces.IObjectCopier(to_copy)
>>> zope.interface.verify.verifyObject(
...     zope.copypastemove.interfaces.IObjectCopier, copier)
True
>>> copier.copyable()
True
>>> copier.copyableTo(repository)
True
>>> copier.copyableTo(repository, name='foo')
True

Let's copy. `copyTo` returns the new name:

>>> copier.copyTo(repository['online'])
ObjectAddedEvent...
'01'

When copying againer, we'll get another name:

>>> copier.copyTo(repository['online'])
ObjectAddedEvent <zeit.cms.repository.unknown.PersistentUnknownResource...>
    Old: None None
    New: <zeit.cms.repository.folder.Folder...> 01-2
...
'01-2'

>>> repository['online'].keys()
['01', '01-2', '2005', '2006', '2007']
>>> len(repository['online']['01'].keys())
53

Let's clean that up again:


>>> site_manager.unregisterHandler(
...     added,
...     (zeit.cms.interfaces.ICMSContent,
...      zope.lifecycleevent.interfaces.IObjectMovedEvent))
True
>>> del repository['online']['01']
>>> del repository['online']['01-2']
>>> import transaction
>>> transaction.commit()

Getting content by unique_id
============================

The `getContent` method of IRepository returns the contained content object
from the unique id:

>>> content = repository.getContent(
...     'http://xml.zeit.de/online/2007/01/Somalia')
>>> content
<zeit.cms.repository.unknown.PersistentUnknownResource...>
>>> content.__parent__
<zeit.cms.repository.folder.Folder...>
>>> content.__parent__.__name__
'01'

An even easier way is adapting to ICMSContent:

>>> zeit.cms.interfaces.ICMSContent(
...     'http://xml.zeit.de/online/2007/01/Somalia')
<zeit.cms.repository.unknown.PersistentUnknownResource...>


A TypeError is raised if anything but a string is passed:

>>> repository.getContent(None)
Traceback (most recent call last):
    ...
TypeError: unique_id: string expected, got ...NoneType...

>>> repository.getContent(123)
Traceback (most recent call last):
    ...
TypeError: unique_id: string expected, got ...int...


A ValueError is raised if the unique_id doesn't start with the configured
prefix of http://xml.zeit.de:

>>> repository.getContent('foo')
Traceback (most recent call last):
    ...
ValueError: The id 'foo' is invalid.

>>> zeit.cms.interfaces.ICMSContent('foo')
Traceback (most recent call last):
    ...
TypeError: ('Could not adapt', 'foo', <InterfaceClass zeit.cms.interfaces.ICMSContent>)

A KeyError is raised if the unique_id does not reference to an existing object:

>>> repository.getContent('http://xml.zeit.de/online/foo')
Traceback (most recent call last):
    ...
KeyError: 'http://xml.zeit.de/online/foo'

>>> zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/foo')
Traceback (most recent call last):
    ...
TypeError: ('Could not adapt', 'http://xml.zeit.de/online/foo', <InterfaceClass zeit.cms.interfaces.ICMSContent>)



Old style paths are supported. When an Id starts with /cms/work it is
considered as valid.

>>> content = repository.getContent('/cms/work/online/2007/01/Somalia')
>>> content.uniqueId
'http://xml.zeit.de/online/2007/01/Somalia'
>>> zeit.cms.interfaces.ICMSContent(
...     '/cms/work/online/2007/01/Somalia').uniqueId
'http://xml.zeit.de/online/2007/01/Somalia'
