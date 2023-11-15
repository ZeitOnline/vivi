from datetime import datetime
import transaction
import zeit.objectlog.interfaces
import zeit.objectlog.testing
import zope.component


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
