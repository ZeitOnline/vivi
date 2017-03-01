# -*- coding: utf-8 -*-

from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.cms.workflow.interfaces import IPublishInfo
from zeit.content.volume.volume import Volume
import mock
import pysolr
import zeit.cms.testing
import zeit.content.volume.testing


class VolumeAdminBrowserTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.volume.testing.ZCML_LAYER
    login_as = 'zmgr:mgrpw'

    def setUp(self):
        super(VolumeAdminBrowserTest, self).setUp()
        volume = Volume()
        volume.year = 2015
        volume.volume = 1
        volume.product = zeit.cms.content.sources.Product(u'ZEI')
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                zeit.cms.content.add.find_or_create_folder('2015', '01')
                self.repository['2015']['01']['ausgabe'] = volume
                content = ExampleContentType()
                content.year = 2015
                content.volume = 1
                content.product = zeit.cms.content.sources.Product(u'ZEI')
                self.repository['testcontent'] = content
                IPublishInfo(self.repository['testcontent']).urgent = True

    def test_view_has_action_buttons(self):
        # Cause the VolumeAdminForm has additional actions
        # check if base class and subclass actions are used.
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/'
               '2015/01/ausgabe/@@admin.html')
        self.assertIn('Apply', self.browser.contents)
        self.assertIn('Publish content', self.browser.contents)

    def test_publish_button_publishes_volume_content(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/'
               '2015/01/ausgabe/@@admin.html')
        solr = mock.Mock()
        self.zca.patch_utility(solr, zeit.solr.interfaces.ISolr)
        solr.search.return_value = pysolr.Results(
            [{'uniqueId': 'http://xml.zeit.de/testcontent'}], 1)
        b.getControl('Publish content of this volume').click()
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                with mock.patch(
                        'zeit.workflow.publish.PublishTask'
                        '.call_publish_script') as script:
                    zeit.workflow.testing.run_publish(
                        zeit.cms.workflow.interfaces.PRIORITY_LOW)
                    script.assert_called_with(['work/testcontent'])
                    self.assertTrue(
                        IPublishInfo(self.repository['testcontent']).published)
