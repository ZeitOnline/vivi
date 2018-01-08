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
        self.solr = mock.Mock()
        self.zca.patch_utility(self.solr, zeit.solr.interfaces.ISolr)
        super(VolumeAdminBrowserTest, self).setUp()
        volume = Volume()
        volume.year = 2015
        volume.volume = 1
        volume.product = zeit.cms.content.sources.Product(u'ZEI')
        zeit.cms.content.add.find_or_create_folder('2015', '01')
        self.repository['2015']['01']['ausgabe'] = volume
        content = ExampleContentType()
        content.year = 2015
        content.volume = 1
        content.product = zeit.cms.content.sources.Product(u'ZEI')
        self.repository['testcontent'] = content
        IPublishInfo(self.repository['testcontent']).urgent = True

    def create_article_with_references(self):
        from zeit.content.article.edit.body import EditableBody
        from zeit.content.article.article import Article
        from zeit.content.article.interfaces import IArticle
        from zeit.content.portraitbox.portraitbox import Portraitbox
        from zeit.content.infobox.infobox import Infobox
        import zeit.cms.browser.form
        article = Article()
        zeit.cms.browser.form.apply_default_values(article, IArticle)
        article.year = 2017
        article.title = u'title'
        article.ressort = u'Deutschland'
        portraitbox = Portraitbox()
        self.repository['portraitbox'] = portraitbox
        body = EditableBody(article, article.xml.body)
        portraitbox_reference = body.create_item('portraitbox', 1)
        portraitbox_reference._validate = mock.Mock()
        portraitbox_reference.references = portraitbox
        infobox = Infobox()
        self.repository['infobox'] = infobox
        infobox_reference = body.create_item('infobox', 2)
        infobox_reference._validate = mock.Mock()
        infobox_reference.references = infobox
        self.repository['image'] = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/2006/DSC00109_2.JPG')
        image_reference = body.create_item('image', 3)
        image_reference.references = image_reference.references.create(
            self.repository['image'])
        image_reference._validate = mock.Mock()
        self.repository['article_with_ref'] = article
        IPublishInfo(article).urgent = True
        return self.repository['article_with_ref']

    def test_view_has_action_buttons(self):
        # Cause the VolumeAdminForm has additional actions
        # check if base class and subclass actions are used.
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/'
               '2015/01/ausgabe/@@admin.html')
        self.assertIn('Apply', self.browser.contents)
        self.assertIn('Publish content', self.browser.contents)

    def publish_content(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/'
               '2015/01/ausgabe/@@publish-all')

    def test_publish_button_publishes_volume_content(self):
        self.solr.search.return_value = pysolr.Results(
            [{'uniqueId': 'http://xml.zeit.de/testcontent'}], 1)
        with mock.patch('zeit.workflow.publish.PublishTask'
                        '.call_publish_script') as script:
            self.publish_content()
            script.assert_called_with(['work/testcontent',
                                       'work/2015/01/ausgabe'])
        self.assertTrue(IPublishInfo(self.repository['testcontent']).published)
        self.assertTrue(
            IPublishInfo(self.repository['2015']['01']['ausgabe']).published)

    def test_referenced_boxes_of_articles_are_published_as_well(self):
        article = self.create_article_with_references()
        self.solr.search.return_value = pysolr.Results(
            [{'uniqueId': article.uniqueId}], 1)
        self.publish_content()
        self.assertTrue(zeit.cms.workflow.interfaces.IPublishInfo(
            self.repository['portraitbox']).published)
        self.assertTrue(zeit.cms.workflow.interfaces.IPublishInfo(
            self.repository['infobox']).published)

    def test_referenced_image_is_not_published(self):
        article = self.create_article_with_references()
        self.solr.search.return_value = pysolr.Results(
            [{'uniqueId': article.uniqueId}], 1)
        self.publish_content()
        self.assertFalse(zeit.cms.workflow.interfaces.IPublishInfo(
            self.repository['image']).published)


class PublishAllContent(zeit.cms.testing.SeleniumTestCase):

    log_errors = True

    layer = zeit.content.volume.testing.WEBDRIVER_LAYER
    login_as = 'zmgr:mgrpw'

    def setUp(self):
        super(PublishAllContent, self).setUp()
        solr = mock.Mock()
        solr.search.return_value = pysolr.Results([], 0)
        self.zca.patch_utility(solr, zeit.solr.interfaces.ISolr)
        volume = Volume()
        volume.year = 2015
        volume.volume = 1
        volume.product = zeit.cms.content.sources.Product(u'ZEI')
        self.repository['ausgabe'] = volume

    def test_publish_shows_spinner(self):
        s = self.selenium
        self.open('/repository/ausgabe/@@admin.html', self.login_as)
        s.click('id=form.actions.publish-all')
        s.waitForElementPresent('css=ol#worklist')
        s.waitForElementPresent('css=li.busy[action=start_job]')
        s.waitForElementNotPresent('css=li.busy[action=start_job]')
        s.assertElementNotPresent('id=publish.errors')
        s.waitForPageToLoad()
        s.click('css=li.workflow')
        # XXX Not stored yet, ZON-4157
        # s.assertText(
        # 'css=.fieldname-logs .widget', '*Collective Publication*')

    def test_multi_publish_errors_are_logged_on_volume(self):
        s = self.selenium
        self.open('/repository/ausgabe/@@admin.html', self.login_as)
        with mock.patch(
                'zeit.workflow.publish.MultiPublishTask.recurse') as recurse:
            recurse.side_effect = RuntimeError('provoked')
            s.click('id=form.actions.publish-all')
            s.waitForElementPresent('css=li.busy[action=start_job]')
            s.waitForElementNotPresent('css=li.busy[action=start_job]')
            s.waitForPageToLoad()
        s.click('css=li.workflow')
        s.assertText('css=.fieldname-logs .widget', '*provoked*')
