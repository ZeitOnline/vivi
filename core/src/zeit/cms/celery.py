import imp
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
    class ZopeLoader(celery.loaders.app.AppLoader):
        """Sets up the Zope environment in the Worker processes."""

        def on_worker_init(self):
            paste_ini = self.app.conf.get('LOGGING_INI')
            if not paste_ini:
                return
            zeit.cms.cli._parse_paste_ini(paste_ini)

            @celery.signals.setup_logging.connect(weak=False)
            def setup_logging(*args, **kw):
                # Logging was already set up by parse_paste_ini above.
                pass

            if self.app.conf.get('DEBUG_WORKER'):
                assert self.app.conf.get('worker_pool') == 'solo'
                self.on_worker_process_init()

        def on_worker_process_init(self):
            import zeit.cms.zope

            conf = self.app.conf
            configfile = conf.get('LOGGING_INI')
            if not configfile:
                raise ValueError(
                    'Celery setting LOGGING_INI not set, '
                    'check celery worker config.')

            settings = zeit.cms.cli._parse_paste_ini(configfile)
            db = zeit.cms.zope.bootstrap(settings)
            conf['ZODB'] = db

        def on_worker_shutdown(self):
            if 'ZODB' in self.app.conf:
                self.app.conf['ZODB'].close()

        def read_configuration(self):
            """Read configuration from either

            * an importable python module, given by its dotted name in
              CELERY_CONFIG_MODULE. Note that this can also be set via
              `$ bin/celery worker --config=<modulename>`. (Also note that
              "celery worker" includes the cwd on the pythonpath.)
            * or a plain python file (given by an absolute path in
              CELERY_CONFIG_FILE)

            If neither env variable is present, no configuration is read, and
            some defaults are used instead that most probably don't work (they
            assume amqp on localhost as broker, for example).
            """
            module = os.environ.get('CELERY_CONFIG_MODULE')
            if module:
                return super(ZopeLoader, self).read_configuration()
            pyfile = os.environ.get('CELERY_CONFIG_FILE')
            if pyfile:
                module = self._import_pyfile(pyfile)
                return celery.utils.collections.DictAttribute(module)

        def _import_pyfile(self, filename):
            """Applies Celery configuration by reading the given python file
            (absolute filename), which unfortunately Celery does not support.

            (Code inspired by flask.config.Config.from_pyfile)
            """
            module = imp.new_module('config')
            module.__file__ = filename
            try:
                with open(filename) as config_file:
                    exec(compile(
                        config_file.read(), filename, 'exec'), module.__dict__)
            except IOError as e:
                e.strerror = 'Unable to load configuration file (%s)' % (
                    e.strerror)
                raise e
            else:
                return module

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
