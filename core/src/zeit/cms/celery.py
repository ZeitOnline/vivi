import logging

log = logging.getLogger(__name__)

try:
    import celery
    import celery.signals
    import celery_longterm_scheduler
    import celery_longterm_scheduler.backend
    import z3c.celery.celery
    import z3c.celery.loader
except ImportError:
    # Provide fake @task decorator, so zeit.web can avoid importing the whole
    # celery machinery (which is somewhat expensive, and totally unnecessary).
    def task(*args, **kw):
        if args:
            return args[0]
        else:
            class Callable:
                def __init__(self, *args, **kwargs):
                    self.args = args
                    self.kwargs = kwargs

                def __call__(self, func):
                    return func

                def delay(self, *args, **kwargs):
                    pass

                def apply_async(self, *args, **kwargs):
                    pass

            return Callable
else:
    class Task(z3c.celery.celery.TransactionAwareTask,
               celery_longterm_scheduler.Task):
        """Combines transactions and proper scheduling.

        Note: the order is important so that scheduling jobs also only happens
        on transaction commit.
        """

        def _assert_json_serializable(self, *args, **kw):
            celery_longterm_scheduler.backend.serialize(args)
            celery_longterm_scheduler.backend.serialize(kw)

    @celery.signals.task_failure.connect
    def on_task_failure(**kwargs):
        log.error("Task %s failed",
                  kwargs.get('task_id', ''),
                  exc_info=kwargs.get('exception'))

    CELERY = celery.Celery(
        __name__, task_cls=Task, loader=z3c.celery.loader.ZopeLoader,
        # Disable argument type checking, it seems broken. Tasks complain about
        # celery-internal kwargs passed to them, etc.
        strict_typing=False)
    # XXX The whole "default app" concept seems a bit murky. However, under
    # waitress this is necessary, otherwise the polling publish dialog tries
    # talking to an unconfigured Celery app. (With gunicorn it works ootb.)
    CELERY.set_default()

    # Export decorator, so client modules can say `@zeit.cms.celery.task()`.
    task = CELERY.task


def route_task(name, args, kwargs, options, task=None, **kw):
    """Make the actual queue name deployment-configurable."""
    assert task is not None

    queue = options.pop('queuename', None)
    if queue is None:
        queue = getattr(task, 'queuename', None)
    if queue is not None:
        queue = task.app.conf['QUEUENAMES'][queue]

    return {'queue': queue}
