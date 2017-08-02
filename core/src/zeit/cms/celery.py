def route_task(name, args, kwargs, options, task=None, **kw):
    """Make the actual queue name deployment-configurable."""
    assert task is not None

    queue = options.pop('queuename', None)
    if queue is None:
        queue = getattr(task, 'queuename', None)
    if queue is not None:
        queue = task.app.conf['QUEUENAMES'][queue]

    return {'queue': queue}
