Workflow XML-Rpc interface
==========================


Setup:

>>> from zope.app.testing.xmlrpc import ServerProxy
>>> server = ServerProxy('http://user:userpw@localhost/')
>>> can_publish = getattr(server, '@@can_publish')
>>> publish = getattr(server, '@@publish')

Let's see if we can publish Somalia:

>>> can_publish('http://xml.zeit.de/online/2007/01/Somalia')
False

Right. Let's set the urgent flag via python[#functionaltest]_:

>>> import zeit.workflow.interfaces
>>> workflow = zeit.workflow.interfaces.IContentWorkflow(
...     repository['online']['2007']['01']['Somalia'])
>>> workflow.urgent = True
>>> import transaction
>>> transaction.commit()
>>> zope.security.management.endInteraction()

Let's see now:

>>> can_publish('http://xml.zeit.de/online/2007/01/Somalia')
True
>>> not not workflow.published
False

Good. Let's publish:

>>> job_id = publish('http://xml.zeit.de/online/2007/01/Somalia')
>>> new_interaction()
>>> tasks.process()
>>> zope.security.management.endInteraction()
>>> workflow.published
True


When we try to publish an object which is not publishable, False will be
returned by publish:

>>> can_publish('http://xml.zeit.de/online/2007/01/eta-zapatero')
False
>>> publish('http://xml.zeit.de/online/2007/01/eta-zapatero')
False


Clean up:

>>> zope.app.component.hooks.setSite(old_site)

.. [#functionaltest] We need to set the site since we're a functional test:

    >>> import zeit.cms.testing
    >>> zeit.cms.testing.set_site()

    Do some imports and get the repository

    >>> import zope.component
    >>> import zeit.cms.repository.interfaces
    >>> import zeit.cms.workflow.interfaces
    >>> repository = zope.component.getUtility(
    ...     zeit.cms.repository.interfaces.IRepository)

    >>> import lovely.remotetask.interfaces
    >>> tasks = zope.component.getUtility(
    ...     lovely.remotetask.interfaces.ITaskService, 'general')

    Setup interaction:

    >>> import zope.publisher.browser
    >>> import zope.security.testing
    >>> import zope.security.management
    >>> def new_interaction():
    ...     principal = zeit.cms.testing.create_interaction()
    >>> new_interaction()
