# -*- coding: utf-8 -*-
from unittest import mock

import pytest
import zope.component

from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.cms.workflow.interfaces import IPublishInfo
from zeit.content.volume.volume import Volume
import zeit.cms.content.field
import zeit.cms.interfaces
import zeit.content.volume.testing
import zeit.find.interfaces


class VolumeAdminBrowserTest(zeit.content.volume.testing.BrowserTestCase):
    login_as = 'zmgr:mgrpw'

    def setUp(self):
        self.elastic = mock.Mock()
        zope.component.getGlobalSiteManager().registerUtility(
            self.elastic, zeit.find.interfaces.ICMSSearch
        )
        super().setUp()
        volume = Volume()
        volume.year = 2015
        volume.volume = 1
        volume.product = zeit.cms.content.sources.Product('ZEI')
        zeit.cms.content.add.find_or_create_folder('2015', '01')
        self.repository['2015']['01']['ausgabe'] = volume
        content = ExampleContentType()
        content.year = 2015
        content.volume = 1
        content.product = zeit.cms.content.sources.Product('ZEI')
        self.repository['testcontent'] = content

    def create_article_with_references(self, mediasync_id=1234, name='article_with_ref'):
        from zeit.content.article.article import Article
        from zeit.content.article.edit.body import EditableBody
        from zeit.content.article.interfaces import IArticle
        from zeit.content.infobox.infobox import Infobox
        from zeit.content.portraitbox.portraitbox import Portraitbox
        import zeit.cms.browser.form

        article = Article()
        zeit.cms.content.field.apply_default_values(article, IArticle)
        article.year = 2017
        article.title = 'title'
        article.ressort = 'Deutschland'
        article.ir_mediasync_id = mediasync_id
        if 'portraitbox' not in self.repository:
            portraitbox = Portraitbox()
            self.repository['portraitbox'] = portraitbox
        body = EditableBody(article, article.xml.find('body'))
        portraitbox_reference = body.create_item('portraitbox', 1)
        portraitbox_reference._validate = mock.Mock()
        portraitbox_reference.references = self.repository['portraitbox']
        if 'infobox' not in self.repository:
            infobox = Infobox()
            self.repository['infobox'] = infobox
        infobox_reference = body.create_item('infobox', 2)
        infobox_reference._validate = mock.Mock()
        infobox_reference.references = self.repository['infobox']
        if 'image' not in self.repository:
            self.repository['image'] = zeit.cms.interfaces.ICMSContent(
                'http://xml.zeit.de/2006/DSC00109_2.JPG'
            )
        image_reference = body.create_item('image', 3)
        image_reference.references = image_reference.references.create(self.repository['image'])
        image_reference._validate = mock.Mock()
        self.repository[name] = article
        return self.repository[name]

    def test_view_has_action_buttons(self):
        # Cause the VolumeAdminForm has additional actions
        # check if base class and subclass actions are used.
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/2015/01/ausgabe/@@admin.html')
        self.assertIn('Apply', self.browser.contents)
        self.assertIn('Publish content', self.browser.contents)

    def publish_content(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/2015/01/ausgabe/@@publish-all')

    def test_publish_button_publishes_volume_content(self):
        connector = zope.component.getUtility(zeit.cms.interfaces.IConnector)
        connector.search_result = ['http://xml.zeit.de/testcontent']
        self.publish_content()
        self.assertTrue(IPublishInfo(self.repository['testcontent']).published)
        self.assertTrue(IPublishInfo(self.repository['2015']['01']['ausgabe']).published)

    def test_referenced_boxes_of_articles_are_published_as_well(self):
        self.create_article_with_references()
        connector = zope.component.getUtility(zeit.cms.interfaces.IConnector)
        connector.search_result = ['http://xml.zeit.de/article_with_ref']
        self.publish_content()
        self.assertTrue(
            zeit.cms.workflow.interfaces.IPublishInfo(self.repository['portraitbox']).published
        )
        self.assertTrue(
            zeit.cms.workflow.interfaces.IPublishInfo(self.repository['infobox']).published
        )

    def test_referenced_premium_audio_objects_are_published_as_well(self):
        self.create_article_with_references(mediasync_id=1234, name='article_1')
        self.create_article_with_references(mediasync_id=1235, name='article_2')
        uniqueIds = ('http://xml.zeit.de/article_1', 'http://xml.zeit.de/article_2')
        connector = zope.component.getUtility(zeit.cms.interfaces.IConnector)
        connector.search_result = list(uniqueIds)
        with mock.patch('zeit.content.volume.volume.Volume.get_audios') as get_audios:
            get_audios.return_value = {
                1234: {
                    'url': 'https://media-delivery.testing.de/d7f6ed45-18b8-45de-9e8f-1aef4e6a33a9.mp3',
                    'duration': 'PT9M7S',
                },
                1235: {
                    'url': 'https://media-delivery.testing.de/d7f6ed45-18b8-45de-9e8f-1aef4e6a33a9.mp3',
                    'duration': 'PT12M',
                },
            }
            b = self.browser
            b.open(
                'http://localhost/++skin++vivi/repository/2015/01/ausgabe/@@create-audio-objects'
            )
        self.publish_content()
        for uniqueId in uniqueIds:
            article = zeit.cms.interfaces.ICMSContent(uniqueId)
            audio = self.repository['premium']['audio']['2015']['01'][
                zeit.cms.content.interfaces.IUUID(article).shortened
            ]
            self.assertTrue(zeit.cms.workflow.interfaces.IPublishInfo(audio).published)

    def test_referenced_image_is_not_published(self):
        self.create_article_with_references()
        connector = zope.component.getUtility(zeit.cms.interfaces.IConnector)
        connector.search_result = ['http://xml.zeit.de/article_with_ref']
        self.publish_content()
        self.assertFalse(
            zeit.cms.workflow.interfaces.IPublishInfo(self.repository['image']).published
        )


class PublishAllContent(zeit.content.volume.testing.SeleniumTestCase):
    log_errors = True
    login_as = 'zmgr:mgrpw'

    def setUp(self):
        super().setUp()
        elastic = mock.Mock()
        elastic.search.return_value = zeit.cms.interfaces.Result()
        zope.component.getGlobalSiteManager().registerUtility(
            elastic, zeit.find.interfaces.ICMSSearch
        )
        volume = Volume()
        volume.year = 2015
        volume.volume = 1
        volume.product = zeit.cms.content.sources.Product('ZEI')
        self.repository['ausgabe'] = volume

    @pytest.mark.xfail(reason='no task to wait for is returned')
    def test_publish_shows_spinner(self):
        s = self.selenium
        self.open('/repository/ausgabe/@@admin.html', self.login_as)
        s.click('id=form.actions.publish-all')
        s.waitForElementPresent('css=ol#worklist')
        s.waitForElementPresent('css=li.busy[action=start_job]')
        s.waitForElementNotPresent('css=li.busy[action=start_job]')
        s.waitForLocation('*/ausgabe')  # wait for reload
        s.assertElementNotPresent('id=publish.errors')
        s.click('css=li.workflow')
        s.assertText('css=.fieldname-logs .widget', '*Collective Publication*')

    @pytest.mark.xfail(reason='no task to wait for is returned')
    def test_multi_publish_errors_are_logged_on_volume(self):
        s = self.selenium
        self.open('/repository/ausgabe/@@admin.html', self.login_as)
        with mock.patch('zeit.workflow.publish.PublishTask.recurse') as recurse:
            recurse.side_effect = RuntimeError('provoked')
            s.click('id=form.actions.publish-all')
            s.waitForElementPresent('css=li.busy[action=start_job]')
            s.waitForElementNotPresent('css=li.busy[action=start_job]')
            s.waitForPageToLoad()
        s.click('css=li.workflow')
        s.assertText('css=.fieldname-logs .widget', '*provoked*')
