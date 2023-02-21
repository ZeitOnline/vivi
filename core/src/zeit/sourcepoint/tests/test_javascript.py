from datetime import datetime
from unittest import mock
from zeit.cms.testing import clock
import transaction
import zeit.cms.testing
import zeit.content.text.text
import zeit.sourcepoint.interfaces
import zeit.sourcepoint.testing
import zope.component


def Text(content=''):
    # XXX Work around clumsy API.
    result = zeit.content.text.text.Text()
    result.text = content
    return result


class JavascriptDownload(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.sourcepoint.testing.LAYER

    def setUp(self):
        super().setUp()
        self.patcher = mock.patch('zeit.sourcepoint.javascript.IPublish')
        self.publish = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        super().tearDown()

    def test_latest_version_sorts_folder_items(self):
        folder = self.repository['sourcepoint']
        folder['msg_20190110.js'] = Text()
        folder['msg_20190113.js'] = Text()
        folder['msg_20190117.js'] = Text()
        folder['msg_201901170815.js'] = Text()
        folder['msg_201901171230.js'] = Text()
        js = zope.component.getUtility(
            zeit.sourcepoint.interfaces.IJavaScript, name='sourcepoint')
        self.assertEqual('http://xml.zeit.de/sourcepoint/msg_201901171230.js',
                         js.latest_version.uniqueId)

    def test_download_no_change_from_latest_version_is_ignored(self):
        folder = self.repository['sourcepoint']
        current = Text('current')
        folder['msg_20190101.js'] = current
        js = zope.component.getUtility(
            zeit.sourcepoint.interfaces.IJavaScript, name='sourcepoint')
        self.assertEqual(1, len(folder))
        with mock.patch.object(js, '_download') as download:
            download.return_value = current.text
            js.update()
        transaction.commit()
        self.assertEqual(1, len(folder))

    def test_download_changed_from_latest_version_stores_new_entry(self):
        folder = self.repository['sourcepoint']
        current = Text('current')
        folder['msg_20190101.js'] = current
        js = zope.component.getUtility(
            zeit.sourcepoint.interfaces.IJavaScript, name='sourcepoint')
        self.assertEqual(1, len(folder))
        with mock.patch.object(js, '_download') as download, clock(
                datetime(2019, 3, 17, 8, 33)):
            download.return_value = 'new'
            js.update()
        transaction.commit()
        self.assertEqual(['msg_20190101.js', 'msg_201903170833.js'],
                         sorted(folder.keys()))
        self.assertEqual(True, self.publish().publish.called)

    def test_download_error_is_ignored(self):
        folder = self.repository['sourcepoint']
        current = Text('current')
        folder['msg_20190101.js'] = current
        js = zope.component.getUtility(
            zeit.sourcepoint.interfaces.IJavaScript, name='sourcepoint')
        self.assertEqual(1, len(folder))
        with mock.patch('requests.get') as request:
            request.side_effect = RuntimeError('provoked')
            js.update()
        transaction.commit()
        self.assertEqual(1, len(folder))

    def test_sweep_keeps_newest(self):
        folder = self.repository['sourcepoint']
        folder['msg_20190110.js'] = Text()
        folder['msg_20190113.js'] = Text()
        folder['msg_20190117.js'] = Text()
        folder['msg_201901170815.js'] = Text()
        folder['msg_201901171230.js'] = Text()
        js = zope.component.getUtility(
            zeit.sourcepoint.interfaces.IJavaScript, name='sourcepoint')
        js.sweep(keep=2)
        self.assertEqual(['msg_201901170815.js', 'msg_201901171230.js'],
                         sorted(folder.keys()))
        self.assertEqual(3, self.publish().retract.call_count)

    def test_sweep_keep_less_than_available_does_nothing(self):
        folder = self.repository['sourcepoint']
        folder['msg_20190110.js'] = Text()
        js = zope.component.getUtility(
            zeit.sourcepoint.interfaces.IJavaScript, name='sourcepoint')
        self.assertEqual(1, len(folder))
        js.sweep(keep=2)
        self.assertEqual(1, len(folder))

    def test_download_addefend_js(self):
        folder = self.repository['addefend']
        folder['addefend_script_20221213.js'] = Text('yesterday')
        js = zope.component.getUtility(
            zeit.sourcepoint.interfaces.IJavaScript, name='addefend')
        self.assertEqual(1, len(folder))
        with mock.patch.object(js, '_download') as download, clock(
                datetime(2022, 12, 14, 13, 13)):
            download.return_value = 'new'
            js.update()
        transaction.commit()
        self.assertEqual([
            'addefend_script_20221213.js', 'addefend_script_202212141313.js'],
            sorted(folder.keys()))
        self.assertEqual(True, self.publish().publish.called)
