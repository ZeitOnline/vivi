# -*- coding: utf-8 -*-
from unittest import mock
import time

from pendulum import datetime
import pendulum
import zope.component

from zeit.cms.workflow.interfaces import IPublishInfo
from zeit.content.article.article import Article
from zeit.content.article.interfaces import IArticle
from zeit.content.volume.volume import Volume
import zeit.cms.content.field
import zeit.cms.interfaces
import zeit.content.volume.testing
import zeit.find.interfaces


class VolumeAdminBrowserTest(zeit.content.volume.testing.BrowserTestCase):
    layer = zeit.content.volume.testing.SQL_WSGI_LAYER
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

    def create_article(self, name='article', mediasync_id=1234):
        article = Article()
        zeit.cms.content.field.apply_default_values(article, IArticle)
        article.year = 2015
        article.volume = 1
        article.product = zeit.cms.content.sources.Product('ZEI')
        article.ir_mediasync_id = mediasync_id
        self.repository[name] = article
        article = self.repository[name]
        IPublishInfo(article).urgent = True
        return article

    def create_article_with_references(
        self, mediasync_id=1234, name='article_with_ref', published=False
    ):
        from zeit.content.article.edit.body import EditableBody
        from zeit.content.infobox.infobox import Infobox
        from zeit.content.portraitbox.portraitbox import Portraitbox

        article = self.create_article(name, mediasync_id)
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
            self.repository['image'] = zeit.content.image.testing.create_local_image(
                'obama-clinton-120x120.jpg'
            )
        image_reference = body.create_item('image', 3)
        image_reference.references = image_reference.references.create(self.repository['image'])
        image_reference._validate = mock.Mock()

        if published:
            article.date_digital_published = datetime(2025, 1, 1)
            info = IPublishInfo(article)
            info.published = True
            info.date_first_released = datetime(2025, 1, 1)

        self.repository[name] = article
        article = self.repository[name]
        return article

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
        self.create_article()
        self.publish_content()
        self.assertTrue(IPublishInfo(self.repository['article']).published)
        self.assertTrue(IPublishInfo(self.repository['2015']['01']['ausgabe']).published)

    def test_referenced_boxes_of_articles_are_published_as_well(self):
        self.create_article_with_references()
        self.publish_content()
        self.assertTrue(
            zeit.cms.workflow.interfaces.IPublishInfo(self.repository['portraitbox']).published
        )
        self.assertTrue(
            zeit.cms.workflow.interfaces.IPublishInfo(self.repository['infobox']).published
        )

    def test_referenced_premium_audio_objects_are_published_as_well(self):
        self.create_article_with_references(mediasync_id=1234, name='article_1')
        self.create_article_with_references(mediasync_id=1235, name='article_2', published=True)

        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/2015/01/ausgabe/@@create-audio-objects')
        self.publish_content()
        uniqueIds = ('http://xml.zeit.de/article_1', 'http://xml.zeit.de/article_2')
        for uniqueId in uniqueIds:
            article = zeit.cms.interfaces.ICMSContent(uniqueId)
            audio = self.repository['premium']['audio']['2015']['01'][
                zeit.cms.content.interfaces.IUUID(article).shortened
            ]
            self.assertTrue(zeit.cms.workflow.interfaces.IPublishInfo(audio).published)

    def test_referenced_image_is_not_published(self):
        self.create_article_with_references()
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

    def create_article(self, name='article'):
        article = Article()
        zeit.cms.content.field.apply_default_values(article, IArticle)
        article.year = 2015
        article.volume = 1
        article.product = zeit.cms.content.sources.Product('ZEI')
        self.repository[name] = article
        article = self.repository[name]
        IPublishInfo(article).urgent = True
        return article

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

    def test_publish_waits_for_all_subtasks(self):
        s = self.selenium
        self.create_article('article1')
        self.create_article('article2')
        connector = zope.component.getUtility(zeit.cms.interfaces.IConnector)
        connector.search_result = ['http://xml.zeit.de/article1', 'http://xml.zeit.de/article2']

        self.open('/repository/ausgabe/@@admin.html', self.login_as)
        with mock.patch('zeit.workflow.publish.PublishTask.recurse') as recurse:

            def delay(_method, start_obj, *_args):
                if start_obj.uniqueId == 'http://xml.zeit.de/article2':
                    time.sleep(1)
                return start_obj

            recurse.side_effect = delay
            s.click('id=form.actions.publish-all')
            s.waitForElementPresent('css=ol#worklist')
            s.waitForElementPresent('css=li.busy[action=start_job]')
            start = pendulum.now('UTC')
            s.waitForElementNotPresent('css=li.busy[action=start_job]')
            assert start.diff(pendulum.now('UTC')).in_seconds() >= 3

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
