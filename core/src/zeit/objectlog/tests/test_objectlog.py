from datetime import datetime, timedelta
from unittest import mock

import transaction
import ZODB.Connection
import ZODB.POSException
import zope.component

import zeit.objectlog.interfaces
import zeit.objectlog.objectlog
import zeit.objectlog.testing


class FakeLogItem:
    # broken LogItem that mimics the cache loss behaviour of ZODB
    def keys(self, *args, **kw):
        raise ZODB.POSException.POSKeyError('foo')


class FakeObjectLog(dict):
    def __setitem__(self, key, _):
        return super().__setitem__(key, FakeLogItem())


class ObjectLog(zeit.objectlog.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.content = zeit.objectlog.testing.Content()
        self.getRootFolder()['content'] = self.content
        transaction.commit()

    def test_timestamp_can_be_overridden(self):
        log = zeit.objectlog.interfaces.ILog(self.content)
        log.log('foo', timestamp=datetime(2012, 6, 12, 13, 49))
        entries = list(log.get_log())
        self.assertEqual(datetime(2012, 6, 12, 13, 49), entries[-1].time)

    def test_delete_removes_entries_of_object(self):
        content2 = zeit.objectlog.testing.Content()
        self.getRootFolder()['content2'] = content2
        transaction.commit()
        zeit.objectlog.interfaces.ILog(self.content).log('one')
        zeit.objectlog.interfaces.ILog(content2).log('two')
        log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        log.delete(content2)
        self.assertEqual(0, len(list(log.get_log(content2))))
        self.assertEqual(1, len(list(log.get_log(self.content))))

    def test_clean(self):
        log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        with mock.patch.object(log, '_object_log', FakeObjectLog()):
            zeit.objectlog.interfaces.ILog(self.content).log('one')
            log.clean(timedelta(days=0))
            self.assertEqual(0, len(list(log.get_log(self.content))))
