from zeit.cms.workflow.interfaces import PRIORITY_DEFAULT


def route_task(name, args, kwargs, options, task=None, **kw):
    """Route the task to a queue using the priority set on it."""
    if task is None:
        return {}
    config = task.app.conf['URGENCY_TO_QUEUE']
    urgency = options.pop('urgency', PRIORITY_DEFAULT)

    return {'queue': config[urgency]}
