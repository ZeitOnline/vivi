import ast
import logging
import os
import os.path
import zeit.cms.cli

log = logging.getLogger(__name__)

try:
    import celery
    import celery.loaders.app
    import celery.signals
    import celery_longterm_scheduler
    import celery_longterm_scheduler.backend
    import z3c.celery.celery
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
    import kombu
    import zeit.cms.zope

    @celery.signals.setup_logging.connect(weak=False)
    def setup_logging(*args, **kw):
        # Logging is set up by ZopeLoader.on_worker_init().
        pass

    class ZopeLoader(celery.loaders.app.AppLoader):
        """Sets up the Zope environment in the Worker processes."""

        def on_worker_init(self):
            """Loads ZCML, which also causes grok to scan (thus import) our
            code, so @task's are registered.
            """
            if 'TESTING' in self.app.conf:
                return  # Setup is handled by the test layer

            zeit.cms.cli.configure(self.app.conf['SETTINGS'])
            zeit.cms.zope.configure_product_config(self.app.conf['SETTINGS'])
            zeit.cms.zope.load_zcml(self.app.conf['SETTINGS']['site_zcml'])

            if self.app.conf.get('worker_pool') == 'solo':
                # When debugging there is no fork, so perform ZODB setup now.
                self.on_worker_process_init()

        def on_worker_process_init(self):
            """Creates ZODB connection *after* forking, otherwise the ZEO
            thread-global locks are copied to each worker, causing deadlock.
            """
            conf = self.app.conf
            db = zeit.cms.zope.create_zodb_database(
                conf['SETTINGS']['zodbconn.uri'])
            conf['ZODB'] = db  # see z3c.celery.TransactionAwareTask

        def on_worker_process_shutdown(self):
            if 'ZODB' in self.app.conf:
                self.app.conf['ZODB'].close()

        def read_configuration(self):
            """Reads configuration from environment variables (names prefixed
            with `celery.`), or a paste.ini file (specified via the environment
            variable CELERY_CONFIG_MODULE, can be overriden with `bin/celery
            worker --config=/path/to/paste.ini`).
            """
            # In client mode, they are already initialized.
            settings = zeit.cms.cli.SETTINGS
            if not settings:  # worker mode
                filename = os.environ.get('CELERY_CONFIG_MODULE')
                if filename:
                    settings = zeit.cms.cli._parse_paste_ini(filename)
                else:
                    settings = os.environ.copy()

            conf = celery.utils.collections.AttributeDict()
            for key, value in settings.items():
                if not key.startswith('celery.'):
                    continue
                conf[key.replace('celery.', '', 1)] = ast.literal_eval(value)
            conf['SETTINGS'] = settings  # see on_worker_init()

            if 'task_queues' in conf:
                queues = []
                for x in conf['task_queues']:
                    if isinstance(x, str):
                        queues.append(kombu.Queue(x))
                    else:
                        queues.append(x)
                conf['task_queues'] = tuple(queues)

            return conf

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
        __name__, task_cls=Task, loader=ZopeLoader,
        # Disable argument type checking, it seems broken. Tasks complain about
        # celery-internal kwargs passed to them, etc.
        strict_typing=False)
    # XXX The whole "default app" concept seems a bit murky. However, under
    # waitress this is necessary, otherwise the polling publish dialog tries
    # talking to an unconfigured Celery app. (With gunicorn it works ootb.)
    CELERY.set_default()

    # Export decorator, so client modules can say `@zeit.cms.celery.task()`.
    task = CELERY.task
