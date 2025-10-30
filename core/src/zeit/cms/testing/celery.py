import threading

import celery.contrib.testing.app
import celery.contrib.testing.worker
import celery.signals
import kombu
import zope.component

import zeit.cms.celery
import zeit.connector.interfaces

from .layer import Layer


class CeleryEagerLayer(Layer):
    def setUp(self):
        zeit.cms.celery.CELERY.conf.task_always_eager = True

    def tearDown(self):
        zeit.cms.celery.CELERY.conf.task_always_eager = False


CELERY_EAGER_LAYER = CeleryEagerLayer()


class CeleryWorkerLayer(Layer):
    """Sets up a thread-layerd celery worker.

    Modeled after celery.contrib.testing.pytest.celery_session_worker and
    celery_session_app.
    """

    queues = (
        'default',
        'publish_homepage',
        'publish_highprio',
        'publish_lowprio',
        'publish_default',
        'publish_timebased',
        'webhook',
    )
    default_queue = 'default'

    def setUp(self):
        self['celery_app'] = zeit.cms.celery.CELERY
        self['celery_previous_config'] = dict(self['celery_app'].conf)

        self['celery_app'].conf.update(celery.contrib.testing.app.DEFAULT_TEST_CONFIG)
        self['celery_app'].conf.update(
            {
                'task_always_eager': False,
                'task_create_missing_queues': False,
                'task_default_queue': self.default_queue,
                'task_queues': [kombu.Queue(q) for q in self.queues],
                'task_send_sent_event': True,  # So we can inspect routing in tests
                'longterm_scheduler_backend': 'memory://',
                'TESTING': True,
                'broker_connection_retry_on_startup': True,  # Avoid deprecation warning
                'ZODB': self['zodbDB-layer'],
            }
        )
        self.reset_celery_app()

        zcml = zope.app.appsetup.appsetup.getConfigContext()
        if zcml.hasFeature('zeit.connector.sql.zope'):
            self._setup_sql_session_isolation()

        self['celery_worker'] = celery.contrib.testing.worker.start_worker(self['celery_app'])
        self['celery_worker'].__enter__()

    def reset_celery_app(self):
        # Reset cached_property values that depend on app.conf values, after
        # config has been changed.
        cls = type(self['celery_app'])
        for name in dir(cls):
            prop = getattr(cls, name)
            if isinstance(prop, kombu.utils.objects.cached_property):
                self['celery_app'].__dict__.pop(name, None)
        # Kludgy way to reset `app.backend`
        self['celery_app']._local = threading.local()

    def _setup_sql_session_isolation(self):
        """Ensure Celery worker threads get their own SQL connection and transaction.

        Workers run in threads and share the scoped_session.
        If worker threads try to use the same connection, they conflict with the main
        thread's savepoint.

        So, let's create thread-local connections for worker threads
        """
        import sqlalchemy.orm
        import zope.sqlalchemy

        main_thread_id = threading.current_thread().ident
        self['_main_thread_id'] = main_thread_id

        # Thread-local storage for worker connections
        self['_worker_connections'] = {}

        def setup_worker_connection(**kwargs):
            """Create a separate SQL connection and session for worker threads."""
            current_thread_id = threading.current_thread().ident

            if current_thread_id == main_thread_id:
                return

            if current_thread_id in self['_worker_connections']:
                return

            connector = zope.component.queryUtility(zeit.connector.interfaces.IConnector)
            if connector is None:
                return
            worker_conn = connector.engine.connect()
            worker_txn = worker_conn.begin()

            worker_session = sqlalchemy.orm.Session(
                bind=worker_conn, join_transaction_mode='create_savepoint'
            )
            zope.sqlalchemy.register(worker_session)

            self['_worker_connections'][current_thread_id] = {
                'connection': worker_conn,
                'transaction': worker_txn,
                'session': worker_session,
            }
            # Replace the scoped_session's thread-local session with our worker session
            connector.session.registry.set(worker_session)

        def cleanup_worker_connection(**kwargs):
            current_thread_id = threading.current_thread().ident

            if current_thread_id == main_thread_id:
                return

            if current_thread_id not in self['_worker_connections']:
                return

            worker_data = self['_worker_connections'][current_thread_id]

            try:
                worker_data['session'].close()
                if connector := zope.component.queryUtility(zeit.connector.interfaces.IConnector):
                    connector.session.remove()
                worker_data['transaction'].rollback()
                worker_data['connection'].close()
            except Exception:
                pass  # ¯\_(ツ)_/¯ I am sure we will be fine

            del self['_worker_connections'][current_thread_id]

        celery.signals.task_prerun.connect(setup_worker_connection, weak=False)
        self['_sql_session_prerun_handler'] = setup_worker_connection

        celery.signals.task_postrun.connect(cleanup_worker_connection, weak=False)
        self['_sql_session_postrun_handler'] = cleanup_worker_connection

    def testSetUp(self):
        # Switch database to the currently active DemoStorage,
        # see zeit.cms.testing.zope.WSGILayer.testSetUp().
        self['celery_app'].conf['ZODB'] = self['zodbDB']

    def testTearDown(self):
        # Ensure no running tasks are still left behind for the next test.
        wait_for_celery()

    def tearDown(self):
        self['celery_worker'].__exit__(None, None, None)
        del self['celery_worker']

        zcml = zope.app.appsetup.appsetup.getConfigContext()
        if zcml.hasFeature('zeit.connector.sql.zope'):
            celery.signals.task_prerun.disconnect(self['_sql_session_prerun_handler'])
            del self['_sql_session_prerun_handler']
            celery.signals.task_postrun.disconnect(self['_sql_session_postrun_handler'])
            del self['_sql_session_postrun_handler']

            if '_worker_connections' in self:
                for thread_id, worker_data in list(self['_worker_connections'].items()):
                    try:
                        worker_data['transaction'].rollback()
                        worker_data['connection'].close()
                    except Exception:
                        pass
                del self['_worker_connections']

            if '_main_thread_id' in self:
                del self['_main_thread_id']

        # This should remove any config additions made by us.
        self['celery_app'].conf.clear()
        self['celery_app'].conf.update(self['celery_previous_config'])
        del self['celery_previous_config']
        self.reset_celery_app()

        del self['celery_app']


def wait_for_celery():
    """For tests on CeleryWorkerLayer: Wait for already enqueued jobs, by
    running another job; since we only have on worker, this works out fine.
    Unfortunately we have to mimic the DAV-cache race condition workaround here
    too and wait an additional 5 seconds, sigh.
    """
    celery_ping.apply_async(countdown=5).get()


# celery.contrib.testing.worker expects a 'ping' task, so it can check that the
# worker is running properly.
@zeit.cms.celery.task(name='celery.ping')
def celery_ping():
    return 'pong'
