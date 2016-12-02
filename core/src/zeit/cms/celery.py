from __future__ import absolute_import
from celery._state import get_current_task
import ConfigParser
import celery
import celery.bootsteps
import celery.loaders.app
import celery.signals
import celery.utils
import imp
import logging
import logging.config
import os
import zope.app.appsetup.interfaces
import zope.app.appsetup.product
import zope.app.server.main
import zope.app.wsgi
import zope.component.hooks
import zope.exceptions.log
import zope.publisher.browser
import zope.security.management


log = logging.getLogger(__name__)


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
            __name__, task_cls=TransactionAwareTask, loader=ZopeLoader,
            strict_typing=False)
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


class TaskFormatter(zope.exceptions.log.Formatter):
    """Provides `task_id` and `task_name` variables for the log format.

    Copy&paste from celery.app.log.TaskFormatter to remove ugly '???'
    placeholders for non-task contexts. Also we inherit from zope.exceptions
    to support `__traceback_info__`.
    """

    def format(self, record):
        task = get_current_task()
        if task and task.request:
            record.__dict__.update(task_id=task.request.id,
                                   task_name=task.name)
        else:
            record.__dict__.setdefault('task_name', '')
            record.__dict__.setdefault('task_id', '')
        return super(TaskFormatter, self).format(record)
