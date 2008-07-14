========
Workflow
========

XXX language mix

Der Workflow ist statusorientiert. Ein Dokument hat allerdings mehrere den
Workflow betreffende Status. Aus Nutzersicht ergeben sich quasi parallele
Aktivitäten[#functionaltest]_.

>>> somalia = repository['online']['2007']['01']['Somalia']
>>> import zeit.workflow.interfaces
>>> workflow = zeit.workflow.interfaces.IContentWorkflow(somalia)
>>> workflow
<zeit.workflow.workflow.ContentWorkflow object at 0x...>

Make sure adapting to IPublishInfo yields the same:

>>> import zeit.cms.workflow.interfaces
>>> zeit.cms.workflow.interfaces.IPublishInfo(somalia)
<zeit.workflow.workflow.ContentWorkflow object at 0x...>

>>> import zope.interface.verify
>>> zope.interface.verify.verifyObject(
...     zeit.workflow.interfaces.IContentWorkflow, workflow)
True
>>> publish = zeit.cms.workflow.interfaces.IPublish(somalia)
>>> publish
<zeit.workflow.publish.Publish object at 0x...>


Activities / States
===================

There are a few simple states. Those states can have three values: yes, no and
not necessary. A document can only be published if all states have a yes or not
nocessary value.

The states are as follows (initially None)

>>> workflow.edited
>>> workflow.corrected
>>> workflow.refined
>>> workflow.images_added


Currently the object cannot be published:

>>> workflow.can_publish()
False

Let's now switch one state after the other and see if we can
publish[#needsinteraction]_:

>>> workflow.edited = True
>>> workflow.can_publish()
False
>>> workflow.corrected = True
>>> workflow.can_publish()
False
>>> workflow.refined = True
>>> workflow.can_publish()
False
>>> workflow.images_added = True
>>> workflow.can_publish()
True

Let's try this with not necessary, too:


>>> workflow.edited = zeit.workflow.interfaces.NotNecessary
>>> workflow.can_publish()
True
>>> workflow.corrected = zeit.workflow.interfaces.NotNecessary
>>> workflow.can_publish()
True
>>> workflow.refined = zeit.workflow.interfaces.NotNecessary
>>> workflow.can_publish()
True
>>> workflow.images_added = zeit.workflow.interfaces.NotNecessary
>>> workflow.can_publish()
True


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
False
>>> workflow.urgent = True
>>> workflow.can_publish()
True


Publishing
==========

If `can_publish` returns False calling the `publish()` method raises an
exception:

>>> workflow.urgent = False
>>> workflow.can_publish()
False
>>> publish.publish()
Traceback (most recent call last):
    ...
PublishingError: Publish pre-conditions not satisifed.


If an object is publish is indicated by the `published` attribute. Also the
date_last_published is set:

>>> workflow.published is None
True
>>> workflow.date_last_published is None
True


Let's publish the object:

>>> workflow.urgent = True
>>> publish.publish()
>>> tasks.process()
>>> workflow.published
True
>>> workflow.date_last_published
datetime.datetime(...)


One can publish more than once to put up a new version:

>>> publish.publish()
>>> tasks.process()
>>> workflow.published
True


Retract
=======

After retracting an object it is no longer publically visible. Note that
retract is unconditinally possible:

>>> workflow.urgent = False
>>> publish.retract()
>>> tasks.process()
>>> workflow.published
False


We did quite some stuff now. Verify the object log:

>>> import zeit.objectlog.interfaces
>>> log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
>>> result = log.get_log(somalia)
>>> import zope.i18n
>>> def print_log(result):
...     for e in result:
...         print e.get_object().uniqueId
...         print '    ', zope.i18n.translate(e.message)
>>> print_log(result)
http://xml.zeit.de/online/2007/01/Somalia
     Edited: yes
http://xml.zeit.de/online/2007/01/Somalia
     Corrected: yes
http://xml.zeit.de/online/2007/01/Somalia
     Refined: yes
http://xml.zeit.de/online/2007/01/Somalia
     Images added: yes
http://xml.zeit.de/online/2007/01/Somalia
     Edited: notnecessary
http://xml.zeit.de/online/2007/01/Somalia
     Corrected: notnecessary
http://xml.zeit.de/online/2007/01/Somalia
     Refined: notnecessary
http://xml.zeit.de/online/2007/01/Somalia
     Images added: notnecessary
http://xml.zeit.de/online/2007/01/Somalia
     Edited: no
http://xml.zeit.de/online/2007/01/Somalia
     Urgent: yes
http://xml.zeit.de/online/2007/01/Somalia
     Urgent: no
http://xml.zeit.de/online/2007/01/Somalia
     Urgent: yes
http://xml.zeit.de/online/2007/01/Somalia
     Publication scheduled
http://xml.zeit.de/online/2007/01/Somalia
     Published
http://xml.zeit.de/online/2007/01/Somalia
     Publication scheduled
http://xml.zeit.de/online/2007/01/Somalia
     Published
http://xml.zeit.de/online/2007/01/Somalia
     Urgent: no
http://xml.zeit.de/online/2007/01/Somalia
     Retracting scheduled
http://xml.zeit.de/online/2007/01/Somalia
     Retracted
     

Time based publish / retract
============================

It is possible to set a publish and/or retract time. This will create a task
which will be executed at the given time.

>>> studivz = repository['online']['2007']['01']['studiVZ']
>>> workflow = zeit.workflow.interfaces.IContentWorkflow(studivz)
>>> not not workflow.published
False
>>> 
>>> workflow.release_period
(None, None)
>>> workflow.urgent = True
>>> workflow.can_publish()
True
>>> import datetime
>>> import pytz
>>> publish_on = (
...     datetime.datetime.now(pytz.UTC) + datetime.timedelta(seconds=3))
>>> workflow.release_period = (publish_on, None)

Processing now doesn't publish because the publish time is not reached, yet:

>>> tasks.process()
>>> not not workflow.published
False

Let's wait a second and process; still not published:

>>> import time
>>> time.sleep(1)
>>> tasks.process()
>>> not not workflow.published
False

We can increase the publish time while a task is active, it will be cancelled
then:

>>> job_id = workflow.publish_job_id
>>> tasks.getStatus(job_id)
'delayed'

>>> publish_on += datetime.timedelta(seconds=1)
>>> workflow.release_period = (publish_on, None)
>>> tasks.getStatus(job_id)
'cancelled'
>>> job_id = workflow.publish_job_id
>>> tasks.getStatus(job_id)
'delayed'
>>> tasks.process()

Waiting another two seconds will publish the object:

>>> time.sleep(2)
>>> tasks.process()
>>> workflow.published
True
>>> tasks.getStatus(job_id)
'completed'


When we set an publication time in the past, the object will just be published
imediately:

>>> orig_publish_date = workflow.date_last_published
>>> publish_on = datetime.datetime(2000, 2, 3, tzinfo=pytz.UTC)
>>> workflow.release_period = (publish_on, None)
>>> tasks.process()
>>> orig_publish_date < workflow.date_last_published
True



Retracting works in the same way:

>>> retract_on = (datetime.datetime.now(pytz.UTC) +
...               datetime.timedelta(seconds=2))
>>> workflow.release_period = (publish_on, retract_on)
>>> tasks.process()
>>> job_id = workflow.retract_job_id
>>> tasks.getStatus(job_id)
'delayed'

Wait:

>>> time.sleep(2)
>>> tasks.process()

The object is rectracted now:

>>> workflow.published
False
>>> tasks.getStatus(job_id)
'completed'

When we just set the same dates again, nothing happens:

>>> workflow.release_period = (publish_on, retract_on)
>>> workflow.published
False
>>> tasks.getStatus(job_id)
'completed'

We can also reset the dates:

>>> workflow.release_period = (None, None)

The actions are logged:

>>> print_log(log.get_log(studivz))
http://xml.zeit.de/online/2007/01/studiVZ
     Urgent: yes
http://xml.zeit.de/online/2007/01/studiVZ
     To be published on 2008 6 13  07:38:48  (job #4)
http://xml.zeit.de/online/2007/01/studiVZ
     Scheduled publication cancelled (job #4).
http://xml.zeit.de/online/2007/01/studiVZ
     To be published on 2008 6 13  07:38:49  (job #5)
http://xml.zeit.de/online/2007/01/studiVZ
     Published
http://xml.zeit.de/online/2007/01/studiVZ
     To be published on 2000 2 3  01:00:00  (job #6)
http://xml.zeit.de/online/2007/01/studiVZ
     Published
http://xml.zeit.de/online/2007/01/studiVZ
     To be retracted on 2008 6 13  07:38:50  (job #7)
http://xml.zeit.de/online/2007/01/studiVZ
     Retracted

The date is actually logged in t he Europe/Belin time zone. Explicitly
compare this and (preventing normalizer):

>>> entry = list(log.get_log(studivz))[5]
>>> u'To be published on 2000 2 3  01:00:00  (job #6)' == (
...    zope.i18n.translate(entry.message))
True

Date first released
===================


When an object is published for the first time, the "date first released" is
set by the workflow engine. We make sure that the date is also copied to the
xml.

>>> import zeit.workflow.interfaces
>>> article = repository['testcontent']
>>> article
<zeit.cms.testcontenttype.testcontenttype.TestContentType object at 0x...>
>>> workflow = zeit.workflow.interfaces.IContentWorkflow(article)
>>> workflow.date_first_released is None
True
>>> workflow.urgent = True
>>> import zeit.cms.workflow.interfaces
>>> publish = zeit.cms.workflow.interfaces.IPublish(article)
>>> publish.publish()
>>> tasks.process()
>>> workflow.date_first_released
datetime.datetime(...)

We expect the value to be in the xml now as well (amongst others):

>>> import lxml.etree
>>> print lxml.etree.tostring(repository['testcontent'].xml, pretty_print=True)
<testtype>
  <head>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="date-last-modified">...</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="date_first_released">...</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/workflow" name="date_last_published">...</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="last_modified_by">zope.user</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/workflow" name="published">yes</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/workflow" name="status">OK</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/meta" name="type">testcontenttype</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/workflow" name="urgent">yes</attribute>
  </head>
  <body/>
</testtype>


When we de-publish the object, the status-flag is removed again:

>>> publish.retract()
>>> tasks.process()
>>> print lxml.etree.tostring(repository['testcontent'].xml, pretty_print=True)
<testtype>
  <head>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="date-last-modified">...</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="date_first_released">...</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/workflow" name="date_last_published">...</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="last_modified_by">zope.user</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/workflow" name="published">no</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/meta" name="type">testcontenttype</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/workflow" name="urgent">yes</attribute>
  </head>
  <body/>
</testtype>


Assets workflow
===============

The asset workflow is also a time based workflow but there are no constraints
in regard to when an asset can be published.

Make UnknownResources an asset to test the workflow:

>>> old_implements = list(zope.interface.implementedBy(
...     zeit.cms.repository.unknown.UnknownResource))
>>> zope.interface.classImplements(
...     zeit.cms.repository.unknown.UnknownResource,
...     zeit.cms.interfaces.IAsset)
>>> workflow = zeit.cms.workflow.interfaces.IPublishInfo(somalia)
>>> workflow
<zeit.workflow.asset.AssetWorkflow object at 0x...>
>>> workflow.can_publish()
True
>>> not not workflow.published
False

Publish somalia:

>>> publish = zeit.cms.workflow.interfaces.IPublish(somalia)
>>> publish.publish()
>>> tasks.process()
>>> workflow.published
True

Retract of course also works:

>>> publish.retract()
>>> tasks.process()
>>> workflow.published
False

Reset the implements:

>>> zope.interface.classImplementsOnly(
...     zeit.cms.repository.unknown.UnknownResource,
...     *old_implements)


Recursive publish
=================

It is possible to publish entire folder structures. This is simply done by
publishing a container.

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
>>> publish.publish()
>>> tasks.process()
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

>>> publish.retract()
>>> tasks.process()
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

The actual publishing happens by external the publish script[#loghandler]_.
Publish the folder again and verify the log:

>>> publish.publish()
>>> tasks.process()
>>> print logfile.getvalue()
Running job ...
Publishing http://xml.zeit.de/online/2007/01
Could not checkout http://xml.zeit.de/online/2007/01
...publish.sh:
Publishing test script
work/online/2007/01
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


Retract script
--------------

The retract script removes files and foldes but it just needs the root to
recursivly remove.

>>> logfile.seek(0)
>>> logfile.truncate()
>>> publish.retract()
>>> tasks.process()
>>> print logfile.getvalue()
Running job ...
Retracting http://xml.zeit.de/online/2007/01
...retract.sh:
Retracting test script
work/online/2007/01
done.
Could not checkout http://xml.zeit.de/online/2007/01


Error handling
--------------

When the publish/retract script fails we'll get an error logged. The script
fails when there is 'JPG' in the input data:

>>> jpg = repository['2006']['DSC00109_2.JPG']
>>> workflow = zeit.workflow.interfaces.IContentWorkflow(jpg)
>>> workflow.urgent = True
>>> publish = zeit.cms.workflow.interfaces.IPublish(jpg)
>>> publish.publish()
>>> import transaction
>>> transaction.commit()
>>> tasks.process()

>>> print_log(log.get_log(jpg))
http://xml.zeit.de/2006/DSC00109_2.JPG
     Urgent: yes
http://xml.zeit.de/2006/DSC00109_2.JPG
     Publication scheduled
http://xml.zeit.de/2006/DSC00109_2.JPG
     Error during publish/retract: ScriptError: ('error\n', 1)


Retry handling
--------------

When there is a ConflictError, publication is tried again up too three times.
Create a subclass for PublishRetractTask which raises a ConflictError when run:

>>> import ZODB.POSException
>>> import zeit.workflow.publish
>>> class ConflictingTask(zeit.workflow.publish.PublishRetractTask):
...     run_count = 0
...     def run(self, obj, info):
...         self.run_count += 1
...         raise ZODB.POSException.ConflictError()

When we run this task it'll be tried three times. After the third run the
conflict error is passed on:

>>> task = ConflictingTask()
>>> input = zeit.workflow.publish.TaskDescription(jpg)
>>> task(None, 1, input)
Traceback (most recent call last):
    ...
ConflictError: database conflict error

>>> task.run_count 
3



[#cleanup]_

.. [#functionaltest] We need to set the site since we're a functional test:

    >>> import zope.app.component.hooks
    >>> old_site = zope.app.component.hooks.getSite()
    >>> zope.app.component.hooks.setSite(getRootFolder())

    Do some imports and get the repository

    >>> import zope.component
    >>> import zeit.cms.repository.interfaces
    >>> import zeit.cms.workflow.interfaces
    >>> repository = zope.component.getUtility(
    ...     zeit.cms.repository.interfaces.IRepository)

    >>> import lovely.remotetask.interfaces
    >>> tasks = zope.component.getUtility(
    ...     lovely.remotetask.interfaces.ITaskService, 'general')

    Also register an tzinfo adapter:



.. [#cleanup] Clean up

    >>> zope.security.management.endInteraction()
    >>> zope.app.component.hooks.setSite(old_site)
    >>> logging.root.removeHandler(log_handler)
    >>> logging.root.setLevel(old_log_level)

.. [#needsinteraction] For publising we need an interacion, i.e. a request

    >>> import zope.publisher.browser
    >>> request = zope.publisher.browser.TestRequest()
    >>> import zope.security.testing
    >>> principal = zope.security.testing.Principal(u'zope.user')
    >>> request.setPrincipal(principal)
    >>> import zope.security.management
    >>> zope.security.management.newInteraction(request)

.. [#loghandler] We need a log handler

    >>> import logging
    >>> import StringIO
    >>> logfile = StringIO.StringIO()
    >>> log_handler = logging.StreamHandler(logfile)
    >>> logging.root.addHandler(log_handler)
    >>> old_log_level = logging.root.level
    >>> logging.root.setLevel(logging.INFO)

