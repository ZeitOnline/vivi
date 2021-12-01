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
PublishingError: Publish pre-conditions not satisifed.


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
set by the workflow engine. We make sure that the date is also copied to the
xml.

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
>>> workflow.date_first_released
DateTime(...)

We expect the value to be in the xml now as well (amongst others):

>>> print(zeit.cms.testing.xmltotext(repository['testcontent'].xml))
<testtype...>
  <head>
    <attribute ns="http://namespaces.zeit.de/CMS/document" name="date-last-modified">...</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/document" name="date_first_released">...</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/workflow" name="date_last_published">...</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/document" name="last_modified_by">zope.user</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/workflow" name="published">yes</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/meta" name="type">testcontenttype</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/workflow" name="urgent">yes</attribute>
    ...
  </head>
  <body/>
</testtype>


When we de-publish the object, the status-flag is removed again:

>>> job_id = publish.retract(background=False)
>>> print(zeit.cms.testing.xmltotext(repository['testcontent'].xml))
<testtype...>
  <head>
    <attribute ns="http://namespaces.zeit.de/CMS/document" name="date-last-modified">...</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/document" name="date_first_released">...</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/workflow" name="date_last_published">...</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/document" name="last_modified_by">zope.user</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/workflow" name="published">no</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/meta" name="type">testcontenttype</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/workflow" name="urgent">yes</attribute>
    ...
  </head>
  <body/>
</testtype>


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
     Published
http://xml.zeit.de/online/2007/01/eta-zapatero
     Retracted



Actual publish retract
======================

Publish script
--------------

Set up a log handler to inspect

>>> import logging
>>> from six import StringIO
>>> logfile = StringIO()
>>> log_handler = logging.StreamHandler(logfile)
>>> logging.root.addHandler(log_handler)
>>> loggers = [None, 'zeit']
>>> oldlevels = {}
>>> for name in loggers:
...     logger = logging.getLogger(name)
...     oldlevels[name] = logger.level
...     logger.setLevel(logging.INFO)


The actual publishing happens by external the publish script.
Publish the folder again and verify the log:

>>> job_id = publish.publish(background=False)
>>> print(logfile.getvalue())
Running job ... for http://xml.zeit.de/online/2007/01/
Publishing http://xml.zeit.de/online/2007/01/
...publish.sh:
publish test script
work/online/2007/01/
work/online/2007/01/4schanzentournee-abgesang
work/online/2007/01/Arbeitsmarktzahlen
work/online/2007/01/EU-Beitritt-rumaenien-bulgarien
work/online/2007/01/Flugsicherheit
work/online/2007/01/Ford-Beerdigung
work/online/2007/01/Gesundheitsreform-Die
work/online/2007/01/Guantanamo
work/online/2007/01/Lateinamerika-Jahresrueckblick
work/online/2007/01/Mehrwertsteuer-Jobs
work/online/2007/01/Merkel-Ansprache
work/online/2007/01/Querdax
work/online/2007/01/Querdax-05-01-07
work/online/2007/01/RUND-Olympique-Marseille
work/online/2007/01/Rosia-Montana
work/online/2007/01/Saarland
work/online/2007/01/Saddam-Anschlaege
work/online/2007/01/Saddam-Kommentar
work/online/2007/01/Saddam-Prozess
work/online/2007/01/Saddam-Verbuendete
work/online/2007/01/Schrempp
work/online/2007/01/Somalia
work/online/2007/01/Somalia-Grill
work/online/2007/01/Somalia-Treffen
work/online/2007/01/Spitzenkandidat-Stoiber
work/online/2007/01/Stern-Umfrage-Bayern
work/online/2007/01/bildergalerie-mehrwertsteuer
work/online/2007/01/bildergalerie-mehrwertsteuer-erhoehung
work/online/2007/01/bildergalerie-spiegel
work/online/2007/01/elterngeld-schlieben
work/online/2007/01/eta-zapatero
work/online/2007/01/eta-zapatero-kommentar
work/online/2007/01/eu-praesidentschaft-gustavsson
work/online/2007/01/finanztest-online-banking
work/online/2007/01/finanztest-online-banking-tipps
work/online/2007/01/flugzeugabsturz-indonesien
work/online/2007/01/index
work/online/2007/01/internationale-presseschau-japan-irak-klima
work/online/2007/01/lebenslagen-01
work/online/2007/01/mein-leben-mit-musik-52
work/online/2007/01/rauchen-verbessert-die-welt
work/online/2007/01/rund-Sprachforschung
work/online/2007/01/saddam-exekution
work/online/2007/01/saddam-grab
work/online/2007/01/saddam-hinrichtung-2006
work/online/2007/01/saddam-luttwak
work/online/2007/01/saddam-nachruf
work/online/2007/01/somalia-donnerstag
work/online/2007/01/somalia-kismayu
work/online/2007/01/studiVZ
work/online/2007/01/teddy-kollek-nachruf
work/online/2007/01/terror-abschuss-schaeuble
work/online/2007/01/thailand-anschlaege
work/online/2007/01/weissrussland-russland-gas
done.
Done http://xml.zeit.de/online/2007/01/ (...s)


Retract script
--------------

The retract script removes files and folders. It removes in the opposite order
of publish:

>>> _ = logfile.seek(0)
>>> _ = logfile.truncate()
>>> job_id = publish.retract(background=False)
>>> print(logfile.getvalue())
Running job ...
Retracting http://xml.zeit.de/online/2007/01/
...publish.sh:
retract test script
work/online/2007/01/weissrussland-russland-gas
work/online/2007/01/thailand-anschlaege
work/online/2007/01/terror-abschuss-schaeuble
work/online/2007/01/teddy-kollek-nachruf
...
work/online/2007/01/Arbeitsmarktzahlen
work/online/2007/01/4schanzentournee-abgesang
work/online/2007/01/
done.
Done http://xml.zeit.de/online/2007/01/ (...s)


Error handling
--------------

When the publish/retract script fails we'll get an error logged. The script
fails when there is 'JPG' in the input data:

>>> jpg = repository['2006']['DSC00109_2.JPG']
>>> workflow = zeit.workflow.interfaces.IContentWorkflow(jpg)
>>> workflow.urgent = True
>>> publish = zeit.cms.workflow.interfaces.IPublish(jpg)
>>> job_id = publish.publish(background=False)
Traceback (most recent call last):
HandleAfterAbort: Error during publish/retract: ScriptError: ('error\n', 1)

>>> print_log(log.get_log(jpg))
http://xml.zeit.de/2006/DSC00109_2.JPG
     Urgent: yes
http://xml.zeit.de/2006/DSC00109_2.JPG
      Error during publish/retract: ScriptError: ('error\n', 1)

Reset the folder implements:

>>> zope.interface.classImplementsOnly(
...     zeit.cms.repository.folder.Folder,
...     *old_implements)



Dependencies
============

Objects can declare publication dependencies. The most prominent example is the
image gallery which references a folder containing images. This folder is
published together with the gallery automatically.

Simple dependencies
+++++++++++++++++++

Let's assume the Somalia article has a dependency on the politik.feed. This
is done via a named adapter to IPublicationDependencies:

>>> class SomaliaFeed(zeit.workflow.dependency.DependencyBase):
...     def get_dependencies(self):
...         if self.context.uniqueId.endswith('Somalia'):
...             return (repository['politik.feed'],)
...         return ()
...
>>> gsm = zope.component.getGlobalSiteManager()
>>> gsm.registerAdapter(
...     SomaliaFeed,
...     (zeit.cms.repository.interfaces.IUnknownResource,),
...     zeit.workflow.interfaces.IPublicationDependencies,
...     name='somalia')

Get the dependencies for the somalia article. There is an adapter which gathers
all the named adapters:

>>> deps = zeit.workflow.interfaces.IPublicationDependencies(
...     somalia).get_dependencies()
>>> deps
[<zeit.cms.syndication.feed.Feed...>]
>>> len(deps)
1
>>> deps[0].uniqueId
u'http://xml.zeit.de/politik.feed'
>>> feed = deps[0]

Currently neither the article nor the image is published:

>>> workflow = zeit.workflow.interfaces.IContentWorkflow(somalia)
>>> workflow.published
False
>>> workflow.urgent = True
>>> workflow.can_publish()
'can-publish-success'
>>> feed_workflow = zeit.workflow.interfaces.IAssetWorkflow(feed)
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
    Object: http://xml.zeit.de/politik.feed
    Master: http://xml.zeit.de/online/2007/01/Somalia
PublishedEvent
    Object: http://xml.zeit.de/online/2007/01/Somalia
    Master: http://xml.zeit.de/online/2007/01/Somalia
PublishedEvent
    Object: http://xml.zeit.de/politik.feed
    Master: http://xml.zeit.de/online/2007/01/Somalia
>>> workflow.published
True
>>> feed_workflow.published
True

Of couse the feed as a log entry:

>>> print_log(log.get_log(feed))
http://xml.zeit.de/politik.feed
     Published


Dependend retract
+++++++++++++++++

Retract does *not* honour dependencies by default:

>>> _ = logfile.seek(0)
>>> _ = logfile.truncate()
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

>>> print(logfile.getvalue())
Running job ...
Retracting http://xml.zeit.de/online/2007/01/Somalia
...publish.sh:
retract test script
work/online/2007/01/Somalia
done.
...

If the dependencies adapter allows it, the dependencies are retracted as well:

>>> SomaliaFeed.retract_dependencies = True
>>> _ = logfile.seek(0)
>>> _ = logfile.truncate()
>>> job_id = publish.retract(background=False)
BeforeRetractEvent
    Object: http://xml.zeit.de/online/2007/01/Somalia
    Master: http://xml.zeit.de/online/2007/01/Somalia
BeforeRetractEvent
    Object: http://xml.zeit.de/politik.feed
    Master: http://xml.zeit.de/online/2007/01/Somalia
RetractedEvent
    Object: http://xml.zeit.de/online/2007/01/Somalia
    Master: http://xml.zeit.de/online/2007/01/Somalia
RetractedEvent
    Object: http://xml.zeit.de/politik.feed
    Master: http://xml.zeit.de/online/2007/01/Somalia
>>> feed_workflow.published
False


Recursive dependencies
++++++++++++++++++++++

When the feed references the article nothing special happens: both are
published when either is published.

Add the reverse dependency:

>>> class FeedSomalia(zeit.workflow.dependency.DependencyBase):
...     def get_dependencies(self):
...         if self.context == feed:
...             return (somalia,)
...         return ()
...
>>> import zeit.cms.syndication.interfaces
>>> gsm.registerAdapter(
...     FeedSomalia,
...     (zeit.cms.syndication.interfaces.IFeed,),
...     zeit.workflow.interfaces.IPublicationDependencies,
...     name='feed')


Publish somalia again:

>>> job_id = publish.publish(background=False)
BeforePublishEvent
    Object: http://xml.zeit.de/online/2007/01/Somalia
    Master: http://xml.zeit.de/online/2007/01/Somalia
BeforePublishEvent
    Object: http://xml.zeit.de/politik.feed
    Master: http://xml.zeit.de/online/2007/01/Somalia
PublishedEvent
    Object: http://xml.zeit.de/online/2007/01/Somalia
    Master: http://xml.zeit.de/online/2007/01/Somalia
PublishedEvent
    Object: http://xml.zeit.de/politik.feed
    Master: http://xml.zeit.de/online/2007/01/Somalia
>>> print_log(log.get_log(feed))
http://xml.zeit.de/politik.feed
     Published
http://xml.zeit.de/politik.feed
     Retracted
http://xml.zeit.de/politik.feed
     Published

>>> gsm.unregisterHandler(pr_handler,
...     (zeit.cms.workflow.interfaces.IWithMasterObjectEvent,))
True



Depending on non workflowed objects
+++++++++++++++++++++++++++++++++++

When there is a dependency on an object which is not publishable by itself it
will be published nevertheles.

Let somalia also depend on the /2007 folder:

>>> class SomaliaFolder(zeit.workflow.dependency.DependencyBase):
...     def get_dependencies(self):
...         if self.context.uniqueId.endswith('Somalia'):
...             return (repository['2007'],)
...         return ()
...
>>> import zeit.cms.syndication.interfaces
>>> gsm.registerAdapter(
...     SomaliaFolder,
...     (zeit.cms.repository.interfaces.IUnknownResource,),
...     zeit.workflow.interfaces.IPublicationDependencies,
...     name='folder')

>>> zeit.workflow.interfaces.IPublicationDependencies(
...     somalia).get_dependencies()
[<zeit.cms.repository.folder.Folder...>,
 <zeit.cms.syndication.feed.Feed...>]

2007 is not published:

>>> not not zeit.cms.workflow.interfaces.IPublishInfo(
...     repository['2007']).published
False

When somalia is published, the folder and its content is also published:

>>> _ = logfile.seek(0)
>>> _ = logfile.truncate()
>>> job_id = publish.publish(background=False)
>>> print(logfile.getvalue())
Running job ...
Publishing http://xml.zeit.de/online/2007/01/Somalia
...publish.sh:
publish test script
work/online/2007/01/Somalia
work/2007/
work/politik.feed
work/2007/01/
work/2007/02/
work/2007/03/
work/2007/test
work/2007/01/LB-Sch-ttler
...
work/2007/02/Vorspann-Dappen
work/2007/02/W-Clear-02
work/2007/03/group/
done.
...

And 2007 is marked as published now:

>>> zeit.cms.workflow.interfaces.IPublishInfo(repository['2007']).published
True

The publication is also logged in the object log:

>>> print_log(log.get_log(repository['2007']))
http://xml.zeit.de/2007/
     Published


Remove the test adapters:

>>> gsm.unregisterAdapter(
...     FeedSomalia,
...     (zeit.cms.syndication.interfaces.IFeed,),
...     zeit.workflow.interfaces.IPublicationDependencies,
...     name='feed')
True
>>> gsm.unregisterAdapter(
...     SomaliaFeed,
...     (zeit.cms.repository.interfaces.IUnknownResource,),
...     zeit.workflow.interfaces.IPublicationDependencies,
...     name='somalia')
True
>>> gsm.unregisterAdapter(
...     SomaliaFolder,
...     (zeit.cms.repository.interfaces.IUnknownResource,),
...     zeit.workflow.interfaces.IPublicationDependencies,
...     name='folder')
True


Clean up
++++++++

>>> logging.root.removeHandler(log_handler)
>>> for name in loggers:
...     logging.getLogger(name).setLevel(oldlevels[name])
