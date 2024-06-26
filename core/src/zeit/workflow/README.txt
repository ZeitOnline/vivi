========
Workflow
========

XXX language mix

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()
>>> import zope.component
>>> import zeit.cms.repository.interfaces
>>> import zeit.cms.workflow.interfaces
>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)


Der Workflow ist statusorientiert. Ein Dokument hat allerdings mehrere den
Workflow betreffende Status. Aus Nutzersicht ergeben sich quasi parallele
Aktivitäten.

>>> somalia = repository['online']['2007']['01']['Somalia']
>>> import zeit.workflow.interfaces
>>> workflow = zeit.workflow.interfaces.IContentWorkflow(somalia)
>>> workflow
<zeit.workflow.workflow.ContentWorkflow...>

Make sure adapting to IPublishInfo yields the same:

>>> import zeit.cms.workflow.interfaces
>>> zeit.cms.workflow.interfaces.IPublishInfo(somalia)
<zeit.workflow.workflow.ContentWorkflow...>

>>> import zope.interface.verify
>>> zope.interface.verify.verifyObject(
...     zeit.workflow.interfaces.IContentWorkflow, workflow)
True
>>> publish = zeit.cms.workflow.interfaces.IPublish(somalia)
>>> publish
<zeit.workflow.publish.Publish...>


Activities / States
===================

There are a few simple states. Those states can have three values: yes, no and
not necessary. A document can only be published if all states have a yes or not
nocessary value.

The states are as follows (initially None)

>>> workflow.edited
>>> workflow.corrected


Currently the object cannot be published:

>>> workflow.can_publish()
'can-publish-error'

For publising we need an interacion, i.e. a request

>>> import zeit.cms.testing
>>> principal = zeit.cms.testing.create_interaction()

Let's now switch one state after the other and see if we can publish:

>>> workflow.edited = True
>>> workflow.can_publish()
'can-publish-error'
>>> workflow.corrected = True
>>> workflow.can_publish()
'can-publish-success'

Let's try this with not necessary, too:


>>> workflow.edited = zeit.workflow.interfaces.NotNecessary
>>> workflow.can_publish()
'can-publish-success'
>>> workflow.corrected = zeit.workflow.interfaces.NotNecessary
>>> workflow.can_publish()
'can-publish-success'
>>> workflow.can_publish()
'can-publish-success'
>>> workflow.can_publish()
'can-publish-success'


Release period
==============

The release period is a time frame where an object is published. This is not
implemented right now.

Urgent
======

Urgent content can be published w/o setting all the states to yes or not
necessary.

>>> workflow.edited = False
>>> workflow.can_publish()
'can-publish-error'
>>> workflow.urgent = True
>>> workflow.can_publish()
'can-publish-success'


Publishing
==========

If `can_publish` returns False calling the `publish()` method raises an
exception:

>>> workflow.urgent = False
>>> workflow.can_publish()
'can-publish-error'
>>> publish.publish(background=False)
Traceback (most recent call last):
    ...
PublishingError: Publish pre-conditions not satisfied.


If an object is publish is indicated by the `published` attribute. Also the
date_last_published is set:

>>> workflow.published
False
>>> workflow.date_last_published is None
True


Let's publish the object:

>>> workflow.urgent = True
>>> job_id = publish.publish(background=False)
>>> workflow.published
True
>>> workflow.date_last_published
DateTime(...)


One can publish more than once to put up a new version:

>>> job_id = publish.publish(background=False)
>>> workflow.published
True


Retract
=======

After retracting an object it is no longer publically visible. Note that
retract is unconditinally possible:

>>> workflow.urgent = False
>>> job_id = publish.retract(background=False)
>>> workflow.published
False


We did quite some stuff now. Verify the object log:

>>> import zeit.objectlog.interfaces
>>> log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
>>> result = log.get_log(somalia)
>>> import zope.i18n
>>> def print_log(result):
...     for e in result:
...         print(e.get_object().uniqueId)
...         print('    ' + zope.i18n.translate(e.message))
>>> print_log(result)
http://xml.zeit.de/online/2007/01/Somalia
     status-edited: yes
http://xml.zeit.de/online/2007/01/Somalia
     status-corrected: yes
http://xml.zeit.de/online/2007/01/Somalia
     status-edited: notnecessary
http://xml.zeit.de/online/2007/01/Somalia
     status-corrected: notnecessary
http://xml.zeit.de/online/2007/01/Somalia
     status-edited: no
http://xml.zeit.de/online/2007/01/Somalia
     Urgent: yes
http://xml.zeit.de/online/2007/01/Somalia
     Urgent: no
http://xml.zeit.de/online/2007/01/Somalia
     Urgent: yes
http://xml.zeit.de/online/2007/01/Somalia
     Published
http://xml.zeit.de/online/2007/01/Somalia
     Published
http://xml.zeit.de/online/2007/01/Somalia
     Urgent: no
http://xml.zeit.de/online/2007/01/Somalia
     Retracted


Date first released
===================


When an object is published for the first time, the "date first released" is
set by the workflow engine.

>>> import zeit.workflow.interfaces
>>> article = repository['testcontent']
>>> article
<zeit.cms.testcontenttype.testcontenttype.ExampleContentType...>
>>> workflow = zeit.workflow.interfaces.IContentWorkflow(article)
>>> workflow.date_first_released is None
True
>>> workflow.urgent = True
>>> import zeit.cms.workflow.interfaces
>>> publish = zeit.cms.workflow.interfaces.IPublish(article)
>>> job_id = publish.publish(background=False)
>>> modified = zeit.cms.workflow.interfaces.IModified(article)
>>> workflow.date_first_released
DateTime(...)
>>> workflow.date_last_published
DateTime(...)
>>> modified.last_modified_by
'zope.user'
>>> workflow.published
True
>>> workflow.urgent
True

When we de-publish the object, the status-flag is removed again:

>>> job_id = publish.retract(background=False)
>>> workflow.published
False


Recursive publish
=================

It is possible to publish entire folder structures. The default for folders
though is that they're not publishable at all:

>>> container = repository['online']['2007']['01']
>>> workflow = zeit.cms.workflow.interfaces.IPublishInfo(container)
>>> workflow
<zeit.workflow.publishinfo.NotPublishablePublishInfo...>
>>> workflow.can_publish()
'can-publish-error'

Let's pretend a folder was editoral content:

>>> import zeit.cms.repository.folder
>>> old_implements = list(zope.interface.implementedBy(
...     zeit.cms.repository.folder.Folder))
>>> zope.interface.classImplements(
...     zeit.cms.repository.folder.Folder,
...     zeit.cms.interfaces.IEditorialContent)

Now recursive publishing works by simply publishing a container.

>>> container = repository['online']['2007']['01']
>>> workflow = zeit.cms.workflow.interfaces.IPublishInfo(container)
>>> publish = zeit.cms.workflow.interfaces.IPublish(container)
>>> bool(workflow.published)
False

Let's have a look a another object. It is not published:

>>> not not zeit.cms.workflow.interfaces.IPublishInfo(
...     container['eta-zapatero']).published
False

Now publish the folder:

>>> workflow.urgent = True
>>> for i in container.values():
...     zeit.cms.workflow.interfaces.IPublishInfo(i).urgent = True
>>> job_id = publish.publish(background=False)
>>> workflow.published
True

Now also all subitems are published:

>>> zeit.cms.workflow.interfaces.IPublishInfo(
...     container['eta-zapatero']).published
True

This is also logged:

>>> result = log.get_log(container['eta-zapatero'])
>>> print_log(result)
http://xml.zeit.de/online/2007/01/eta-zapatero
    Urgent: yes
http://xml.zeit.de/online/2007/01/eta-zapatero
    Published


Retracting is also possible recursivly:

>>> job_id = publish.retract(background=False)
>>> workflow.published
False

Make sure the subobjects are also retracted:

>>> zeit.cms.workflow.interfaces.IPublishInfo(
...     container['eta-zapatero']).published
False


This is also logged:

>>> result = log.get_log(container['eta-zapatero'])
>>> print_log(result)
http://xml.zeit.de/online/2007/01/eta-zapatero
    Urgent: yes
http://xml.zeit.de/online/2007/01/eta-zapatero
    Published
http://xml.zeit.de/online/2007/01/eta-zapatero
    Retracted

Dependencies
============

Objects can declare publication dependencies. The most prominent example is the
image gallery which references a folder containing images. This folder is
published together with the gallery automatically.

Simple dependencies
+++++++++++++++++++

Let's assume the Somalia article has a dependency on another article. This
is done via a named adapter to IPublicationDependencies:

>>> class SomaliaFeed(zeit.cms.workflow.dependency.DependencyBase):
...     def get_dependencies(self):
...         if self.context.uniqueId.endswith('Somalia'):
...             return (repository['2006']['49']['Zinsen'],)
...         return ()
...
>>> gsm = zope.component.getGlobalSiteManager()
>>> gsm.registerAdapter(
...     SomaliaFeed,
...     (zeit.cms.repository.interfaces.IUnknownResource,),
...     zeit.cms.workflow.interfaces.IPublicationDependencies,
...     name='somalia')

Get the dependencies for the somalia article. There is an adapter which gathers
all the named adapters:

>>> deps = zeit.cms.workflow.interfaces.IPublicationDependencies(
...     somalia).get_dependencies()
>>> deps
[<zeit.cms.repository.unknown...>]
>>> len(deps)
1
>>> deps[0].uniqueId
'http://xml.zeit.de/2006/49/Zinsen'
>>> feed = deps[0]

Currently neither the article nor the image is published:

>>> workflow = zeit.cms.workflow.interfaces.IPublishInfo(somalia)
>>> workflow.published
False
>>> workflow.urgent = True
>>> workflow.can_publish()
'can-publish-success'
>>> feed_workflow = zeit.cms.workflow.interfaces.IPublishInfo(feed)
>>> feed_workflow.urgent = True
>>> not not feed_workflow.published
False

When we publish somalia now the feed is published
automatically:

We register event handlers to all the publish/retract events to see the master

>>> def pr_handler(event):
...     print(type(event).__name__)
...     print('    Object: %s' % event.object.uniqueId)
...     print('    Master: %s' % event.master.uniqueId)
>>> gsm.registerHandler(pr_handler,
...     (zeit.cms.workflow.interfaces.IWithMasterObjectEvent,))

>>> publish = zeit.cms.workflow.interfaces.IPublish(somalia)
>>> job_id = publish.publish(background=False)
BeforePublishEvent
    Object: http://xml.zeit.de/online/2007/01/Somalia
    Master: http://xml.zeit.de/online/2007/01/Somalia
BeforePublishEvent
    Object: http://xml.zeit.de/2006/49/Zinsen
    Master: http://xml.zeit.de/online/2007/01/Somalia
PublishedEvent
    Object: http://xml.zeit.de/online/2007/01/Somalia
    Master: http://xml.zeit.de/online/2007/01/Somalia
PublishedEvent
    Object: http://xml.zeit.de/2006/49/Zinsen
    Master: http://xml.zeit.de/online/2007/01/Somalia
>>> workflow.published
True
>>> feed_workflow.published
True

Of couse the feed as a log entry:

>>> print_log(log.get_log(feed))
http://xml.zeit.de/2006/49/Zinsen
     Urgent: yes
http://xml.zeit.de/2006/49/Zinsen
     Published


Dependend retract
+++++++++++++++++

Retract does *not* honour dependencies by default:

>>> job_id = publish.retract(background=False)
BeforeRetractEvent
    Object: http://xml.zeit.de/online/2007/01/Somalia
    Master: http://xml.zeit.de/online/2007/01/Somalia
RetractedEvent
    Object: http://xml.zeit.de/online/2007/01/Somalia
    Master: http://xml.zeit.de/online/2007/01/Somalia
>>> feed_workflow.published
True

Make sure the file would actually have been removed:

If the dependencies adapter allows it, the dependencies are retracted as well:

>>> SomaliaFeed.retract_dependencies = True
>>> job_id = publish.retract(background=False)
BeforeRetractEvent
    Object: http://xml.zeit.de/online/2007/01/Somalia
    Master: http://xml.zeit.de/online/2007/01/Somalia
BeforeRetractEvent
    Object: http://xml.zeit.de/2006/49/Zinsen
    Master: http://xml.zeit.de/online/2007/01/Somalia
RetractedEvent
    Object: http://xml.zeit.de/online/2007/01/Somalia
    Master: http://xml.zeit.de/online/2007/01/Somalia
RetractedEvent
    Object: http://xml.zeit.de/2006/49/Zinsen
    Master: http://xml.zeit.de/online/2007/01/Somalia
>>> feed_workflow.published
False


Recursive dependencies
++++++++++++++++++++++

When the feed references the article nothing special happens: both are
published when either is published.

Add the reverse dependency:

>>> class FeedSomalia(zeit.cms.workflow.dependency.DependencyBase):
...     def get_dependencies(self):
...         if self.context == feed:
...             return (somalia,)
...         return ()
...
>>> import zeit.content.cp.interfaces
>>> gsm.registerAdapter(
...     FeedSomalia,
...     (zeit.content.cp.interfaces.IFeed,),
...     zeit.cms.workflow.interfaces.IPublicationDependencies,
...     name='feed')


Publish somalia again:

>>> job_id = publish.publish(background=False)
BeforePublishEvent
    Object: http://xml.zeit.de/online/2007/01/Somalia
    Master: http://xml.zeit.de/online/2007/01/Somalia
BeforePublishEvent
    Object: http://xml.zeit.de/2006/49/Zinsen
    Master: http://xml.zeit.de/online/2007/01/Somalia
PublishedEvent
    Object: http://xml.zeit.de/online/2007/01/Somalia
    Master: http://xml.zeit.de/online/2007/01/Somalia
PublishedEvent
    Object: http://xml.zeit.de/2006/49/Zinsen
    Master: http://xml.zeit.de/online/2007/01/Somalia
>>> print_log(log.get_log(feed))
http://xml.zeit.de/2006/49/Zinsen
    Urgent: yes
http://xml.zeit.de/2006/49/Zinsen
    Published
http://xml.zeit.de/2006/49/Zinsen
    Retracted
http://xml.zeit.de/2006/49/Zinsen
    Published

>>> gsm.unregisterHandler(pr_handler,
...     (zeit.cms.workflow.interfaces.IWithMasterObjectEvent,))
True
