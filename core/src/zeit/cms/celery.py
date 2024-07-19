from contextlib import contextmanager
import ast
import logging
import os
import os.path

import zeit.cms.cli


log = logging.getLogger(__name__)

try:
    from opentelemetry.instrumentation.celery import CeleryInstrumentor
    from opentelemetry.instrumentation.celery import utils as otel_celery
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
    import bugsnag
    import kombu
    import opentelemetry.trace
    import prometheus_client
    import zope.app.appsetup.appsetup
    import zope.component

    from zeit.cms.tracing import anonymize
    import zeit.cms.interfaces
    import zeit.cms.relstorage
    import zeit.cms.tracing
    import zeit.cms.zope

    @celery.signals.setup_logging.connect(weak=False)
    def setup_logging(*args, **kw):
        # Logging is set up by ZopeLoader.read_configuration().
        pass

    class ZopeLoader(celery.loaders.app.AppLoader):
        """Sets up the Zope environment in the Worker processes."""

        def on_worker_init(self):
            """Loads ZCML, which also causes grok to scan (thus import) our
            code, so @task's are registered.
            """
            if 'TESTING' in self.app.conf:
                return  # Setup is handled by the test layer

            zeit.cms.zope.configure_product_config(self.app.conf['SETTINGS'])
            zeit.cms.zope.load_zcml(self.app.conf['SETTINGS'])
            prefix = 'bugsnag.'
            bugsnag_conf = {
                key.replace(prefix, '', 1): value
                for key, value in self.app.conf['SETTINGS'].items()
                if key.startswith(prefix)
            }
            zeit.cms.bugsnag.configure(bugsnag_conf)

            port = int(os.environ.get('CELERY_PROMETHEUS_PORT', 0))
            if port:
                registry = zope.component.getUtility(zeit.cms.interfaces.IPrometheusRegistry)
                prometheus_client.start_http_server(port, registry=registry)

            if self.app.conf.get('worker_pool') == 'solo':
                # When debugging there is no fork, so perform ZODB setup now.
                self.on_worker_process_init()

        def on_worker_process_init(self):
            """Creates ZODB connection *after* forking, psql connections are
            not fork-safe.
            """
            conf = self.app.conf
            db = zeit.cms.zope.create_zodb_database(conf['SETTINGS']['zodbconn.uri'])
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
            if not settings:  # worker or other celery command
                settings = {}
                filename = os.environ.get('CELERY_CONFIG_MODULE')
                if filename:
                    settings.update(zeit.cms.cli._parse_paste_ini(filename))
                settings.update(os.environ)
                zcml = zope.app.appsetup.appsetup.getConfigContext()
                if zcml is None or not zcml.hasFeature('zeit.cms.testing'):
                    zeit.cms.cli.configure(settings)

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

    class Task(z3c.celery.celery.TransactionAwareTask, celery_longterm_scheduler.Task):
        """Combines transactions and proper scheduling.

        Note: the order is important so that scheduling jobs also only happens
        on transaction commit.
        """

        def _assert_json_serializable(self, *args, **kw):
            celery_longterm_scheduler.backend.serialize(args)
            celery_longterm_scheduler.backend.serialize(kw)

        @contextmanager
        def transaction(self, principal_id):
            span = opentelemetry.trace.get_current_span()
            span.set_attribute('enduser.id', anonymize(principal_id))
            with super().transaction(principal_id):
                yield

    @celery.signals.task_failure.connect
    def on_task_failure(**kw):
        log.error(
            'Task %s (%s) failed',
            kw.get('sender', '<unknown task>'),
            kw.get('task_id', ''),
            exc_info=kw.get('exception'),
        )
        bugsnag.notify(
            kw['exception'],
            traceback=kw['traceback'],
            context=kw['sender'].name,
            extra_data={'task_id': kw['task_id'], 'args': kw['args'], 'kw': kw['kwargs']},
        )

    CELERY = celery.Celery(
        __name__,
        task_cls=Task,
        loader=ZopeLoader,
        # Disable argument type checking, it seems broken. Tasks complain about
        # celery-internal kwargs passed to them, etc.
        strict_typing=False,
    )
    # XXX The whole "default app" concept seems a bit murky. However, under
    # waitress this is necessary, otherwise the polling publish dialog tries
    # talking to an unconfigured Celery app. (With gunicorn it works ootb.)
    CELERY.set_default()

    # Export decorator, so client modules can say `@zeit.cms.celery.task()`.
    task = CELERY.task

    # NOTE: Ordering matters here. We rely on the fact that celery signal
    # handlers are called in the order they are defined, so that our nested
    # context is attached after the upstream one, and detached before.
    @celery.signals.task_postrun.connect(weak=False)
    def remove_samplerate(*args, **kw):
        task = otel_celery.retrieve_task(kw)
        token, _ = otel_celery.retrieve_span(task, 'zeit.cms.tracing')
        if token is not None:
            opentelemetry.context.detach(token)
        otel_celery.detach_span(task, 'zeit.cms.tracing')

    CeleryInstrumentor().instrument()

    @celery.signals.task_prerun.connect(weak=False)
    def apply_samplerate(*args, **kw):
        context = zeit.cms.tracing.apply_samplerate_productconfig(
            'zeit.cms.relstorage',
            'zeit.cms',
            'samplerate-zodb',
            opentelemetry.context.get_current(),
        )
        context = zeit.cms.tracing.apply_samplerate_productconfig(
            'zeit.connector.postgresql.tracing', 'zeit.cms', 'samplerate-sql', context
        )
        context = zeit.cms.tracing.apply_samplerate_productconfig(
            'zeit.workflow.publish', 'zeit.cms', 'samplerate-publish', context
        )
        if context is not None:
            token = opentelemetry.context.attach(context)
            task = otel_celery.retrieve_task(kw)
            # This is a bit of a semantic misuse, but mechanically it's
            # exactly what we want: store this bit of data on the task object.
            otel_celery.attach_span(task, 'zeit.cms.tracing', (token, None))
