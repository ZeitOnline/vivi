from unittest import mock

import zope.copypastemove.interfaces

from zeit.cms.checkout.helper import checked_out
from zeit.cms.repository.folder import Folder
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

    def test_does_not_delete_on_add(self):
        self.repository['second'] = ExampleContentType()
        self.assertFalse(self.delete.called)


class MoveContentBaseTest(zeit.cms.testing.ZeitCmsTestCase):
    def test_move_event_has_correct_oldparent(self):
        move = mock.Mock()
        zope.component.getGlobalSiteManager().registerHandler(
            move, (zope.lifecycleevent.IObjectMovedEvent,)
        )
        self.repository['oldparent'] = Folder()
        self.repository['oldparent']['testcontent'] = ExampleContentType()
        content = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/oldparent/testcontent')
        zope.copypastemove.interfaces.IObjectMover(content).moveTo(self.repository, 'changed')
        event = move.call_args[0][0]
        self.assertEqual(self.repository['oldparent'], event.oldParent)

    def test_move_content_preserves_objectlog_even_in_root_folder(self):
        with checked_out(self.repository['testcontent']):
            # checkout to create log entry in workflowlog
            pass
        original = self.repository['testcontent']
        original_log = list(zeit.objectlog.interfaces.ILog(original).get_log())
        zope.copypastemove.interfaces.IObjectMover(original).moveTo(self.repository, 'changed')
        changed = self.repository['changed']
        changed_log = list(zeit.objectlog.interfaces.ILog(changed).get_log())
        self.assertEqual(len(original_log), len(changed_log))
        for old, copied in zip(original_log, changed_log, strict=False):
            self.assertEqual(old.message, copied.message)
            self.assertEqual(old.time, copied.time)

    def test_move_content_preserves_objectlog(self):
        self.repository['folder'] = Folder()
        self.repository['folder']['testcontent'] = ExampleContentType()
        with checked_out(self.repository['folder']['testcontent']):
            # checkout to create log entry in workflowlog
            pass
        original = self.repository['folder']['testcontent']
        original_log = list(zeit.objectlog.interfaces.ILog(original).get_log())
        zope.copypastemove.interfaces.IObjectMover(original).moveTo(
            self.repository['folder'], 'changed'
        )
        changed = self.repository['folder']['changed']
        changed_log = list(zeit.objectlog.interfaces.ILog(changed).get_log())
        self.assertEqual(len(original_log), len(changed_log))
        for old, copied in zip(original_log, changed_log, strict=False):
            self.assertEqual(old.message, copied.message)
            self.assertEqual(old.time, copied.time)
