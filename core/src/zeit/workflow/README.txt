========
Workflow
========

XXX language mix

Der Workflow ist statusorientiert. Ein Dokument hat allerdings mehrere den
Workflow betreffende Status. Aus Nutzersicht ergeben sich quasi parallele
Aktivitäten[1]_.

>>> somalia = repository['online']['2007']['01']['Somalia']
>>> workflow = zeit.cms.workflow.interfaces.IPublish(somalia)
>>> import zeit.workflow.interfaces
>>> zeit.workflow.interfaces.IWorkflow.providedBy(workflow)
True
>>> import zope.interface.verify
>>> zope.interface.verify.verifyObject(
...     zeit.workflow.interfaces.IWorkflow, workflow)
True

Activities / States
===================

There are a few simple states. Those states can have three values: yes, no and
not necessary. A document can only be published if all states have a yes or not
nocessary value.

The states are as follows:

>>> workflow.edited
False
>>> workflow.corrected
False
>>> workflow.refined
False
>>> workflow.images_added
False


Currently the object cannot be published:

>>> workflow.can_publish()
False

Let's now switch one state after the other and see if we can publish:

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
>>> workflow.publish()
Traceback (most recent call last):
    ...
PublishingError: Publish pre-conditions not satisifed.


If an object is publish is indicated by the `published` attribute.

>>> workflow.published
False


Let's publish the object[3]_:

>>> workflow.urgent = True
>>> workflow.publish()

>>> workflow.published
True

One can publish more than once to put up a new version:

>>> workflow.publish()
>>> workflow.published
True


Retract
=======

After retracting an object it is no longer publically visible. Note that
retract is unconditinally possible:

>>> workflow.urgent = False
>>> workflow.retract()
>>> workflow.published
False


That was the workflow[2]_.

.. [1] We need to set the site since we're a functional test:

    >>> import zope.app.component.hooks
    >>> old_site = zope.app.component.hooks.getSite()
    >>> zope.app.component.hooks.setSite(getRootFolder())

    Do some imports and get the repository

    >>> import zope.component
    >>> import zeit.cms.repository.interfaces
    >>> import zeit.cms.workflow.interfaces
    >>> repository = zope.component.getUtility(
    ...     zeit.cms.repository.interfaces.IRepository)


.. [2] Clean up

    >>> zope.security.management.endInteraction()
    >>> zope.app.component.hooks.setSite(old_site)


.. [3] For publising we need an interacion, i.e. a request

    >>> import zope.publisher.browser
    >>> request = zope.publisher.browser.TestRequest()
    >>> import zope.security.testing
    >>> principal = zope.security.testing.Principal(u'hans')
    >>> request.setPrincipal(principal)
    >>> import zope.security.management
    >>> zope.security.management.newInteraction(request)
