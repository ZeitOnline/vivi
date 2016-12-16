from zeit.cms.workflow.interfaces import PRIORITY_DEFAULT


def route_task(name, args, kwargs, options, task=None, **kw):
    """Route the task to a queue using the priority set on it."""
    assert task is not None

    urgency = options.pop('urgency', None)
    if urgency is None:
        urgency = getattr(task, 'urgency', PRIORITY_DEFAULT)

    config = task.app.conf['URGENCY_TO_QUEUE']

    return {'queue': config[urgency]}
