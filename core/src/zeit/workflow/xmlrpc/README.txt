Workflow XML-Rpc interface
==========================


Setup:

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()
>>> import zope.component
>>> import zeit.cms.repository.interfaces
>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)

>>> import zeit.workflow.testing
>>> import transaction
>>> def run_tasks():
...     zeit.workflow.testing.run_tasks()
...     transaction.abort()

>>> from zeit.cms.webtest import ServerProxy
>>> server = ServerProxy('http://user:userpw@localhost/', layer['wsgi_app'])
>>> can_publish = getattr(server, '@@can_publish')
>>> publish = getattr(server, '@@publish')
>>> retract = getattr(server, '@@retract')

Let's see if we can publish Somalia:

>>> can_publish('http://xml.zeit.de/online/2007/01/Somalia')
False

Right. Let's set the urgent flag via python:

>>> import zeit.workflow.interfaces
>>> _ = zeit.cms.testing.create_interaction()
>>> workflow = zeit.workflow.interfaces.IContentWorkflow(
...     repository['online']['2007']['01']['Somalia'])
>>> workflow.urgent = True
>>> zope.security.management.endInteraction()

Let's see now:

>>> can_publish('http://xml.zeit.de/online/2007/01/Somalia')
True
>>> not not workflow.published
False

Good. Let's publish:

>>> job_id = publish('http://xml.zeit.de/online/2007/01/Somalia')
>>> run_tasks()
>>> workflow.published
True


When we try to publish an object which is not publishable, False will be
returned by publish:

>>> can_publish('http://xml.zeit.de/online/2007/01/eta-zapatero')
False
>>> publish('http://xml.zeit.de/online/2007/01/eta-zapatero')
False

Retract:

>>> job_id = retract('http://xml.zeit.de/online/2007/01/Somalia')
>>> run_tasks()
>>> workflow.published
False


Helper for timebased jobs:

>>> bool(workflow.retract_job_id)
False
>>> server.setup_timebased_jobs('http://xml.zeit.de/online/2007/01/Somalia')
False

>>> import pendulum
>>> _ = zeit.cms.testing.create_interaction()
>>> workflow.release_period = (None, pendulum.now().add(days=1))
>>> zope.security.management.endInteraction()

>>> server.setup_timebased_jobs('http://xml.zeit.de/online/2007/01/Somalia')
True
>>> bool(workflow.retract_job_id)
True
