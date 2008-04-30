========
Workflow
========

XXX language mix

Der Workflow ist statusorientiert. Ein Dokument hat allerdings mehrere den
Workflow betreffende Status. Aus Nutzersicht ergeben sich quasi parallele
Aktivitäten[#functionaltest]_.

>>> somalia = repository['online']['2007']['01']['Somalia']
>>> workflow = zeit.workflow.interfaces.IWorkflowStatus(somalia)
>>> import zeit.workflow.interfaces
>>> import zope.interface.verify
>>> zope.interface.verify.verifyObject(
...     zeit.workflow.interfaces.IWorkflowStatus, workflow)
True
>>> publish = zeit.cms.workflow.interfaces.IPublish(somalia)

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
>>> result = list(log.get_log(somalia))
>>> import zope.i18n
>>> for e in result:
...     print e.get_object().uniqueId
...     print '    ', zope.i18n.translate(e.message)
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
     



Date first released
-------------------


When an object is published for the first time, the "date first released" is
set by the workflow engine. We make sure that the date is also copied to the
xml.

>>> import zeit.workflow.interfaces
>>> article = repository['testcontent']
>>> article
<zeit.cms.testcontenttype.testcontenttype.TestContentType object at 0x...>
>>> workflow = zeit.workflow.interfaces.IWorkflowStatus(article)
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
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="date_first_released">...</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/workflow" name="date_last_published">...</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="DAV:" name="getlastmodified">...</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="last_modified_by">zope.user</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/workflow" name="published">yes</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="DAV:" name="resourcetype">testcontenttype</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/workflow" name="status">OK</attribute>
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
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="date_first_released">...</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/workflow" name="date_last_published">...</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="DAV:" name="getlastmodified">...</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="last_modified_by">zope.user</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/workflow" name="published">no</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="DAV:" name="resourcetype">testcontenttype</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/workflow" name="urgent">yes</attribute>
  </head>
  <body/>
</testtype>


That was the workflow[#cleanup]_.

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


.. [#cleanup] Clean up

    >>> zope.security.management.endInteraction()
    >>> zope.app.component.hooks.setSite(old_site)


.. [#needsinteraction] For publising we need an interacion, i.e. a request

    >>> import zope.publisher.browser
    >>> request = zope.publisher.browser.TestRequest()
    >>> import zope.security.testing
    >>> principal = zope.security.testing.Principal(u'zope.user')
    >>> request.setPrincipal(principal)
    >>> import zope.security.management
    >>> zope.security.management.newInteraction(request)
