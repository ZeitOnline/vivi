from unittest import mock

import zope.copypastemove.interfaces

from zeit.cms.checkout.helper import checked_out
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.cms.testing


class TestDeleteObjectlog(zeit.cms.testing.ZeitCmsTestCase):
    def setUp(self):
        super().setUp()
        self.patch = mock.patch('zeit.objectlog.objectlog.ObjectLog.delete')
        self.delete = self.patch.start()

    def tearDown(self):
        self.patch.stop()
        super().tearDown()

    def test_deletes_on_delete(self):
        del self.repository['testcontent']
        self.assertTrue(self.delete.called)

    def test_deletes_on_move(self):
        renamer = zope.copypastemove.interfaces.IContainerItemRenamer(self.repository)
        renamer.renameItem('testcontent', 'moved')
        self.assertTrue(self.delete.called)
        self.assertEqual(
            'http://xml.zeit.de/testcontent', self.delete.call_args[0][0].referenced_object
        )

    def test_does_not_delete_on_add(self):
        self.repository['second'] = ExampleContentType()
        self.assertFalse(self.delete.called)


class MoveContentBaseTest(zeit.cms.testing.ZeitCmsTestCase):
    def test_move_event_has_correct_oldparent(self):
        move = mock.Mock()
        zope.component.getGlobalSiteManager().registerHandler(
            move, (zope.lifecycleevent.IObjectMovedEvent,)
        )
        content = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        zope.copypastemove.interfaces.IObjectMover(content).moveTo(self.repository, 'changed')
        event = move.call_args[0][0]
        self.assertEqual(self.repository['online']['2007']['01'], event.oldParent)

    def test_move_content_preserves_objectlog(self):
        with checked_out(self.repository['testcontent']):
            # checkout to create log entry in workflowlog
            pass
        original = self.repository['testcontent']
        original_log = list(zeit.objectlog.interfaces.ILog(original).get_log())
        zope.copypastemove.interfaces.IObjectMover(original).moveTo(self.repository, 'changed')
        changed = self.repository['changed']
        changed_log = list(zeit.objectlog.interfaces.ILog(changed).get_log())
        self.assertEqual(len(original_log), len(changed_log))
        for old, copied in zip(original_log, changed_log):
            self.assertEqual(old.message, copied.message)
            self.assertEqual(old.time, copied.time)
