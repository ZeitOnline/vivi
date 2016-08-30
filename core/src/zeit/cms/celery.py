from __future__ import absolute_import
import ConfigParser
import ZODB.POSException
import celery
import celery.bootsteps
import celery.loaders.app
import celery.signals
import grokcore.component as grok
import imp
import logging
import logging.config
import os
import transaction
import zope.app.appsetup.interfaces
import zope.app.appsetup.product
import zope.app.server.main
import zope.app.wsgi
import zope.component.hooks
import zope.publisher.browser
import zope.security.management


log = logging.getLogger(__name__)


class TransactionAwareTask(celery.Task):
    """Wraps every Task execution in a transaction begin/commit/abort.
    If 'ZOPE_PRINCIPAL' is set in the celery configuration, also sets up a
    zope.security interaction.

    (Code inspired by gocept.runner.runner.MainLoop)
    """

    abstract = True  # Base class. Don't register as an excecutable task.

    @classmethod
    def bind(self, app):
        # Unfortunately, Celery insists on setting up everything at import
        # time, which doesn't work for our clients, since the Zope
        # product-configuration is not available then. Thus we perform an
        # additional bind() in the configure_celery_client event handler.
        if not app.configure_done:
            return app
        return super(TransactionAwareTask, self).bind(app)

    def __call__(self, *args, **kw):
        old_site = zope.component.hooks.getSite()
        zope.component.hooks.setSite(self.app.conf['ZOPE_APP'])

        self.transaction_begin()
        try:
            result = super(TransactionAwareTask, self).__call__(*args, **kw)
        except Exception, e:
            self.transaction_abort()
            raise e
        finally:
            zope.component.hooks.setSite(old_site)

        try:
            self.transaction_commit()
        except ZODB.POSException.ConflictError, e:
            log.info('Retrying due to %s', str(e))
            self.transaction_abort()
            raise self.retry(countdown=1)

        return result

    def transaction_begin(self):
        transaction.begin()
        if self.principal:
            request = zope.publisher.browser.TestRequest()
            request.setPrincipal(self.principal)
            zope.security.management.newInteraction(request)

    def transaction_abort(self):
        transaction.abort()
        if self.principal:
            zope.security.management.endInteraction()

    def transaction_commit(self):
        transaction.commit()
        if self.principal:
            zope.security.management.endInteraction()

    @property
    def principal(self):
        principal_id = self.app.conf.get('ZOPE_PRINCIPAL')
        if not principal_id:
            return None
        auth = zope.component.getUtility(
            zope.app.security.interfaces.IAuthentication)
        return auth.getPrincipal(principal_id)


class ZopeCelery(celery.Celery):
    """Handles configuration for the two main parts of the Celery machinery:

    1. Client processes (i.e. normal Zope processes, that want to enqueue
    celery jobs). These need to have the same Celery configuration as the
    Worker (so they put the jobs into the same broker the worker reads from).
    This is implemented by setting the path to the celery config file as the
    product configuration `zeit.cms:celery-config`.

    2. Worker process (main process which spawns the actual workers). Gets path
    to the config file from the environment variable `CELERY_WORKER_CONFIG`.
    (This is also how we differentiate between worker and client mode: only the
    worker must receive this environment variable.)

    ZopeCelery adds support for the following keys to the celery config file:

    * ZOPE_CONF (required): Absolute path to the `zope.conf` file. From this,
      both the main process and the individual worker processes will set up the
      Zope enviroment.

    * LOGGING_INI (optional): Absolute path to an ini file containing a
      `[loggers]` and related sections. If given, logging will be set up
      according to that file instead of Celery's built-in rules. (Typically:
      the paste.ini file used for the Client processes)

    * ZOPE_PRINCIPAL (optional): Principal ID under which the workers will
      process each job.

    """

    def __init__(self):
        super(ZopeCelery, self).__init__(
            __name__, task_cls=TransactionAwareTask, loader=ZopeLoader)
        self.is_worker = False
        self.configure_done = False
        self.maybe_configure_as_worker()

    def maybe_configure_as_worker(self):
        config = os.environ.get('CELERY_WORKER_CONFIG')
        if not config:
            return

        self.is_worker = True
        self.config_from_pyfile(config)
        self.steps['worker'].add(ZopeBootstep)

        paste_ini = self.conf.get('LOGGING_INI')
        if paste_ini:
            @celery.signals.setup_logging.connect(weak=False)
            def setup_logging(*args, **kw):
                """Makes the loglevel finely configurable via a config file."""
                # Code inspired by pyramid.paster.setup_logging().
                parser = ConfigParser.ConfigParser()
                parser.read([paste_ini])
                if parser.has_section('loggers'):
                    config_file = os.path.abspath(paste_ini)
                    logging.config.fileConfig(config_file, dict(
                        __file__=config_file,
                        here=os.path.dirname(config_file)))

    def config_from_pyfile(self, filename):
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
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise e
        self.config_from_object(module)
        self.configure_done = True


class ZopeLoader(celery.loaders.app.AppLoader):
    """Sets up the Zope environment in the Worker processes.

    (Code inspired by gocept.runner.runner.init)
    """

    def on_worker_process_init(self):
        conf = self.app.conf
        configfile = conf.get('ZOPE_CONF')
        if not configfile:
            raise ValueError(
                'Celery setting ZOPE_CONF not set, check in '
                'CELERY_CONFIG=%s' % os.environ.get('CELERY_CONFIG'))

        options = zope.app.server.main.load_options(['-C', configfile])
        zope.app.appsetup.product.setProductConfigurations(
            options.product_config)
        db = zope.app.wsgi.config(
            configfile, schemafile=os.path.join(
                os.path.dirname(zope.app.server.main.__file__), 'schema.xml'))
        conf['ZOPE_APP'] = db.open().root()['Application']
        conf['ZODB'] = db

    def on_worker_shutdown(self):
        if 'ZODB' in self.app.conf:
            self.app.conf['ZODB'].close()


class ZopeBootstep(celery.bootsteps.StartStopStep):
    """Sets up the Zope environment in the Worker main process.

    We do this mainly so grok scans and imports our packages, which guarantees
    that all celery-tasks decorated functions in our code will be registered.

    Note: even though Celery documentation calls this a "worker bootstep",
    it actually runs in the main process.
    """

    def start(self, parent):
        parent.app.loader.on_worker_process_init()

    def stop(self, parent):
        parent.app.loader.on_worker_shutdown()


@grok.subscribe(zope.app.appsetup.interfaces.IDatabaseOpenedWithRootEvent)
def configure_celery_client(event):
    """Sets up celery configuration in Client processes."""
    if CELERY.is_worker:
        # ZopeCelery.maybe_configure_as_worker() has already configured celery,
        # so we don't need to do it _again_ when this event is later triggered
        # by ZopeLoader.on_worker_process_init().
        return
    config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
    CELERY.config_from_pyfile(config['celery-config'])
    for task in CELERY.tasks.values():
        task.bind(CELERY)


CELERY = ZopeCelery()
# Export decorator, so client modules can simply say `@zeit.cms.celery.task()`.
task = CELERY.task
