from unittest import mock

from pendulum import datetime
import time_machine
import transaction
import zope.component

import zeit.cms.testing
import zeit.content.text.text
import zeit.kilkaya.interfaces
import zeit.kilkaya.testing


def Text(content=''):
    # XXX Work around clumsy API.
    result = zeit.content.text.text.Text()
    result.text = content
    return result


class JsonDownload(zeit.cms.testing.FunctionalTestCase):
    layer = zeit.kilkaya.testing.LAYER

    def setUp(self):
        super().setUp()
        self.patcher = mock.patch('zeit.kilkaya.json.IPublish')
        self.publish = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        super().tearDown()

    def test_latest_version_sorts_folder_items(self):
        folder = self.repository['kilkaya-teaser-splittests']
        folder['splittests_20190110.json'] = Text()
        folder['splittests_20190113.json'] = Text()
        folder['splittests_20190117.json'] = Text()
        folder['splittests_201901170815.json'] = Text()
        folder['splittests_201901171230.json'] = Text()
        js = zope.component.getUtility(zeit.kilkaya.interfaces.IJson, name='teaser_splittests')
        self.assertEqual(
            'http://xml.zeit.de/kilkaya-teaser-splittests/splittests_201901171230.json',
            js.latest_version.uniqueId,
        )

    def test_download_no_change_from_latest_version_is_ignored(self):
        folder = self.repository['kilkaya-teaser-splittests']
        current = Text('current')
        folder['splittests_20190101.json'] = current
        js = zope.component.getUtility(zeit.kilkaya.interfaces.IJson, name='teaser_splittests')
        self.assertEqual(1, len(folder))
        with mock.patch.object(js, '_download') as download:
            download.return_value = current.text
            js.update()
        transaction.commit()
        self.assertEqual(1, len(folder))

    @time_machine.travel(datetime(2019, 3, 17, 9, 33))
    def test_download_changed_from_latest_version_stores_new_entry(self):
        folder = self.repository['kilkaya-teaser-splittests']
        current = Text('current')
        folder['splittests_20190101.json'] = current
        js = zope.component.getUtility(zeit.kilkaya.interfaces.IJson, name='teaser_splittests')
        self.assertEqual(1, len(folder))
        with mock.patch.object(js, '_download') as download:
            download.return_value = 'new'
            js.update()
        transaction.commit()
        self.assertEqual(
            ['splittests_20190101.json', 'splittests_201903170933.json'], sorted(folder.keys())
        )
        self.assertEqual(True, self.publish().publish.called)

    def test_download_error_is_ignored(self):
        folder = self.repository['kilkaya-teaser-splittests']
        current = Text('current')
        folder['splittests_20190101.json'] = current
        js = zope.component.getUtility(zeit.kilkaya.interfaces.IJson, name='teaser_splittests')
        self.assertEqual(1, len(folder))
        with mock.patch('requests.get') as request:
            request.side_effect = RuntimeError('provoked')
            js.update()
        transaction.commit()
        self.assertEqual(1, len(folder))

    def test_sweep_keeps_newest(self):
        folder = self.repository['kilkaya-teaser-splittests']
        folder['splittests_20190110.json'] = Text()
        folder['splittests_20190113.json'] = Text()
        folder['splittests_20190117.json'] = Text()
        folder['splittests_201901170815.json'] = Text()
        folder['splittests_201901171230.json'] = Text()
        js = zope.component.getUtility(zeit.kilkaya.interfaces.IJson, name='teaser_splittests')
        js.sweep(keep=2)
        self.assertEqual(
            ['splittests_201901170815.json', 'splittests_201901171230.json'], sorted(folder.keys())
        )
        self.assertEqual(3, self.publish().retract.call_count)

    def test_sweep_keep_less_than_available_does_nothing(self):
        folder = self.repository['kilkaya-teaser-splittests']
        folder['splittests_20190110.json'] = Text()
        js = zope.component.getUtility(zeit.kilkaya.interfaces.IJson, name='teaser_splittests')
        self.assertEqual(1, len(folder))
        js.sweep(keep=2)
        self.assertEqual(1, len(folder))
